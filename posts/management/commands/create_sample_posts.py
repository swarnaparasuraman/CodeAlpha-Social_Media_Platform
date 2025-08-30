from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from posts.models import Post, Comment
from social.models import Like
import requests
import random
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create sample posts with images and interactions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='Number of posts to create (default: 20)',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of sample users to create (default: 10)',
        )

    def handle(self, *args, **options):
        num_posts = options['posts']
        num_users = options['users']
        
        self.stdout.write('Creating sample data...')
        
        # Create sample users
        users = self.create_sample_users(num_users)
        
        # Create sample posts
        posts = self.create_sample_posts(users, num_posts)
        
        # Add interactions
        self.add_interactions(users, posts)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {num_posts} posts and {num_users} users!')
        )

    def create_sample_users(self, num_users):
        """Create sample users with profiles."""
        users = []
        usernames = [
            'alex_photographer', 'sarah_travels', 'mike_fitness', 'emma_foodie',
            'david_tech', 'lisa_artist', 'john_nature', 'anna_fashion',
            'chris_music', 'maya_books', 'tom_sports', 'zoe_design',
            'ryan_gaming', 'nina_yoga', 'sam_cooking', 'jade_dance'
        ]
        
        for i in range(num_users):
            username = usernames[i % len(usernames)] + f"_{i+1}"
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password='samplepass123',
                    first_name=username.split('_')[0].title(),
                    last_name=username.split('_')[1].title()
                )
                
                # Update profile
                profile = user.profile
                profile.bio = self.get_sample_bio(username)
                profile.location = random.choice([
                    'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Miami, FL',
                    'Seattle, WA', 'Austin, TX', 'Denver, CO', 'Portland, OR'
                ])
                profile.save()
                
            users.append(user)
            
        return users

    def create_sample_posts(self, users, num_posts):
        """Create sample posts with content and images."""
        posts = []
        
        post_contents = [
            "Just captured this amazing sunset! 🌅 #photography #nature",
            "Coffee and coding session ☕️ #developer #productivity",
            "Weekend vibes at the beach 🏖️ #weekend #relaxation",
            "New recipe turned out amazing! 🍝 #cooking #foodie",
            "Morning workout complete 💪 #fitness #motivation",
            "Art exhibition was incredible today 🎨 #art #culture",
            "Hiking through the mountains 🏔️ #hiking #adventure",
            "Late night reading session 📚 #books #learning",
            "Concert was absolutely amazing! 🎵 #music #livemusic",
            "Yoga practice in the park 🧘‍♀️ #yoga #mindfulness",
            "Game night with friends 🎮 #gaming #friends",
            "Fresh flowers from the garden 🌸 #gardening #spring",
            "Delicious brunch spot discovered! 🥞 #brunch #foodie",
            "New design project completed ✨ #design #creative",
            "Running through the city streets 🏃‍♂️ #running #fitness",
            "Cozy evening at home 🏠 #home #comfort",
            "Street art tour was fascinating 🎭 #streetart #urban",
            "Farmers market haul 🥕 #organic #healthy",
            "Sunset picnic in the park 🧺 #picnic #sunset",
            "New tech gadget unboxing 📱 #tech #gadgets"
        ]
        
        for i in range(num_posts):
            author = random.choice(users)
            content = random.choice(post_contents)
            
            # Create post
            post = Post.objects.create(
                author=author,
                content=content,
                created_at=self.get_random_date()
            )
            
            # Add random image (using placeholder service)
            if random.choice([True, False]):  # 50% chance of having an image
                try:
                    image_url = f"https://picsum.photos/800/600?random={i}"
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        image_content = ContentFile(response.content)
                        post.image.save(f'post_{post.id}.jpg', image_content, save=True)
                except Exception as e:
                    self.stdout.write(f"Could not download image for post {post.id}: {e}")
            
            posts.append(post)
            
        return posts

    def add_interactions(self, users, posts):
        """Add likes and comments to posts."""
        for post in posts:
            # Add random likes
            num_likes = random.randint(0, min(len(users), 15))
            likers = random.sample(users, num_likes)
            
            for liker in likers:
                Like.objects.get_or_create(
                    user=liker,
                    post=post
                )
            
            # Update likes count
            post.likes_count = Like.objects.filter(post=post).count()
            
            # Add random comments
            num_comments = random.randint(0, 5)
            comment_texts = [
                "Amazing! 😍", "Love this!", "So beautiful!", "Great shot!",
                "Incredible work!", "This is awesome!", "Perfect timing!",
                "Stunning!", "Well done!", "Fantastic!", "Beautiful capture!",
                "This made my day!", "Absolutely gorgeous!", "Wow!"
            ]
            
            for _ in range(num_comments):
                commenter = random.choice(users)
                comment_text = random.choice(comment_texts)
                
                Comment.objects.create(
                    post=post,
                    author=commenter,
                    content=comment_text,
                    created_at=self.get_random_date(post.created_at)
                )
            
            # Update comments count
            post.comments_count = Comment.objects.filter(post=post).count()
            post.save()

    def get_sample_bio(self, username):
        """Generate sample bio based on username."""
        bios = {
            'alex_photographer': '📸 Capturing moments that matter | Travel & Portrait Photography',
            'sarah_travels': '✈️ Wanderlust | 30 countries and counting | Travel blogger',
            'mike_fitness': '💪 Personal Trainer | Fitness enthusiast | Helping you reach your goals',
            'emma_foodie': '🍕 Food lover | Recipe creator | Sharing delicious discoveries',
            'david_tech': '👨‍💻 Software Engineer | Tech enthusiast | Building the future',
            'lisa_artist': '🎨 Digital Artist | Creative soul | Art is life',
            'john_nature': '🌲 Nature lover | Hiking enthusiast | Protecting our planet',
            'anna_fashion': '👗 Fashion designer | Style inspiration | Sustainable fashion advocate',
            'chris_music': '🎵 Musician | Producer | Music is my language',
            'maya_books': '📚 Bookworm | Literature lover | Always reading something new',
            'tom_sports': '⚽ Sports fanatic | Weekend warrior | Game day every day',
            'zoe_design': '✨ UX Designer | Creating beautiful experiences | Design thinking',
            'ryan_gaming': '🎮 Gamer | Streamer | Level up your life',
            'nina_yoga': '🧘‍♀️ Yoga instructor | Mindfulness coach | Find your zen',
            'sam_cooking': '👨‍🍳 Chef | Culinary artist | Flavor is everything',
            'jade_dance': '💃 Dancer | Choreographer | Movement is poetry'
        }
        
        base_username = '_'.join(username.split('_')[:-1])
        return bios.get(base_username, '✨ Living life to the fullest | Creating memories')

    def get_random_date(self, after_date=None):
        """Generate a random date within the last 30 days."""
        if after_date:
            start_date = after_date
            end_date = timezone.now()
        else:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
        
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between + 1)
        random_seconds = random.randrange(24 * 60 * 60)
        
        return start_date + timedelta(days=random_days, seconds=random_seconds)
