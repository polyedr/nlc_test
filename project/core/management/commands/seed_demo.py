import random
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Audio, Page, PageContent, Video


class Command(BaseCommand):
    help = "Seed demo data: pages, videos, audios, and page-content links."

    def add_arguments(self, parser):
        # Number of pages to create
        parser.add_argument(
            "--pages",
            type=int,
            default=5,
            help="How many pages to create (default: 5).",
        )
        # Min and max items per page
        parser.add_argument(
            "--min-items",
            type=int,
            default=2,
            help="Min content items per page (default: 2).",
        )
        parser.add_argument(
            "--max-items",
            type=int,
            default=5,
            help="Max content items per page (default: 5).",
        )
        # Total pool of videos/audios from which pages will reference
        parser.add_argument(
            "--videos",
            type=int,
            default=8,
            help="How many Video objects to create in the pool (default: 8).",
        )
        parser.add_argument(
            "--audios",
            type=int,
            default=8,
            help="How many Audio objects to create in the pool (default: 8).",
        )
        # Whether to wipe previous demo data
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing demo data before seeding.",
        )
        # Seed for reproducibility
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Random seed for reproducible data (default: None).",
        )

    def handle(self, *args, **options):
        pages_count: int = options["pages"]
        min_items: int = options["min_items"]
        max_items: int = options["max_items"]
        videos_pool: int = options["videos"]
        audios_pool: int = options["audios"]
        do_flush: bool = options["flush"]
        seed_value = options["seed"]

        # Basic validations
        if min_items < 1:
            self.stderr.write(self.style.ERROR("--min-items must be >= 1"))
            return
        if max_items < min_items:
            self.stderr.write(self.style.ERROR("--max-items must be >= --min-items"))
            return

        # Set random seed if provided, for deterministic runs
        if seed_value is not None:
            random.seed(seed_value)

        # Optionally flush old data
        if do_flush:
            self._flush_demo()

        # Create core pools of content
        with transaction.atomic():
            videos = self._create_videos(videos_pool)
            audios = self._create_audios(audios_pool)
            pages = self._create_pages(pages_count)

            # Attach content to pages in ordered fashion
            self._attach_content_to_pages(pages, videos, audios, min_items, max_items)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {pages_count} pages, {len(videos)} videos, {len(audios)} audios."
            )
        )

    # ---------------------------
    # Helper methods
    # ---------------------------

    def _flush_demo(self):
        """Delete all demo data. Keep order: PageContent -> Video/Audio -> Page."""
        # NOTE: We are aggressive here; if you need selective cleanup, adjust filters.
        self.stdout.write("Flushing existing demo data...")
        PageContent.objects.all().delete()
        Video.objects.all().delete()
        Audio.objects.all().delete()
        Page.objects.all().delete()

    def _create_videos(self, count: int) -> List[Video]:
        """Create a pool of Video objects."""
        # Keep URLs simple and deterministic for testing/demo purposes.
        videos = []
        for i in range(1, count + 1):
            videos.append(
                Video(
                    title=f"Video #{i}",
                    counter=random.randint(0, 3),  # small initial counters
                    video_url=f"https://cdn.example.com/videos/v{i}.mp4",
                    subtitles_url=f"https://cdn.example.com/subtitles/v{i}.vtt",
                )
            )
        Video.objects.bulk_create(videos)
        return list(Video.objects.order_by("id"))

    def _create_audios(self, count: int) -> List[Audio]:
        """Create a pool of Audio objects."""
        texts = [
            "Short transcript about testing API endpoints.",
            "Longer transcript regarding background tasks and atomic updates.",
            "Transcript focusing on pagination and serializer design.",
            "Notes on generic relations and content modeling.",
            "Discussion on DRF viewsets and routers.",
            "Details about Celery eager mode for unit tests.",
            "Thoughts on admin inlines and search fields.",
            "A paragraph on database indexing and ordering.",
        ]
        audios = []
        for i in range(1, count + 1):
            audios.append(
                Audio(
                    title=f"Audio #{i}",
                    counter=random.randint(0, 3),
                    transcript=random.choice(texts),
                )
            )
        Audio.objects.bulk_create(audios)
        return list(Audio.objects.order_by("id"))

    def _create_pages(self, count: int) -> List[Page]:
        """Create a list of Page objects."""
        pages = []
        for i in range(1, count + 1):
            pages.append(Page(title=f"Page {i}"))
        Page.objects.bulk_create(pages)
        return list(Page.objects.order_by("id"))

    def _attach_content_to_pages(
        self,
        pages: List[Page],
        videos: List[Video],
        audios: List[Audio],
        min_items: int,
        max_items: int,
    ):
        """Attach content to pages in a random order with explicit positions."""
        # Build ContentTypes once for efficiency
        ct_video = ContentType.objects.get_for_model(Video)
        ct_audio = ContentType.objects.get_for_model(Audio)

        pc_bulk = []
        # Round-robin-ish selection to ensure variety across pages
        v_idx, a_idx = 0, 0

        for page in pages:
            # Decide how many items this page will have
            items_count = random.randint(min_items, max_items)

            # Mix of videos and audios per page
            mixed_items = []
            for _ in range(items_count):
                # 50/50 choose video or audio if available
                pick_video = bool(random.getrandbits(1))
                if pick_video and videos:
                    v = videos[v_idx % len(videos)]
                    mixed_items.append(("video", v.id))
                    v_idx += 1
                elif audios:
                    a = audios[a_idx % len(audios)]
                    mixed_items.append(("audio", a.id))
                    a_idx += 1
                else:
                    # If one pool is empty (shouldn't happen), fall back to the other
                    if videos:
                        v = videos[v_idx % len(videos)]
                        mixed_items.append(("video", v.id))
                        v_idx += 1
                    elif audios:
                        a = audios[a_idx % len(audios)]
                        mixed_items.append(("audio", a.id))
                        a_idx += 1

            # Shuffle to simulate arbitrary order on page
            random.shuffle(mixed_items)

            # Create PageContent rows with an explicit position starting from 1
            position = 1
            for kind, obj_id in mixed_items:
                if kind == "video":
                    pc_bulk.append(
                        PageContent(
                            page=page,
                            content_type=ct_video,
                            object_id=obj_id,
                            position=position,
                        )
                    )
                else:
                    pc_bulk.append(
                        PageContent(
                            page=page,
                            content_type=ct_audio,
                            object_id=obj_id,
                            position=position,
                        )
                    )
                position += 1

        PageContent.objects.bulk_create(pc_bulk)
