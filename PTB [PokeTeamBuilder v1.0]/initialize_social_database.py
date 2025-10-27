"""
Initialize Social Community Database
Creates the social features database and adds a demo user.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from features.social_community_hub import CommunityManager


def main():
    """Initialize the social database."""
    print("Initializing Social Community Database...")
    
    # Create community manager (this will create the database)
    community_manager = CommunityManager()
    
    print("✓ Database tables created")
    
    # Create demo user
    print("\nCreating demo user...")
    demo_user_id = community_manager.register_user(
        username="demo_user",
        email="demo@pokemonteambuilder.com",
        display_name="Demo Trainer",
        password="demo123",
        bio="Welcome to the Pokemon Community Hub! This is a demo account for testing."
    )
    
    if demo_user_id:
        print(f"✓ Demo user created successfully!")
        print(f"  Username: demo_user")
        print(f"  Password: demo123")
        print(f"  User ID: {demo_user_id}")
    else:
        print("⚠ Demo user already exists or registration failed")
    
    # Create a few more demo users for testing
    print("\nCreating additional demo users...")
    
    demo_users = [
        {
            "username": "ash_ketchum",
            "email": "ash@pokemon.com",
            "display_name": "Ash Ketchum",
            "password": "pikachu123",
            "bio": "Gotta catch 'em all! Pokemon Master in training."
        },
        {
            "username": "misty_waterflower",
            "email": "misty@pokemon.com",
            "display_name": "Misty",
            "password": "starmie123",
            "bio": "Water-type Pokemon trainer and Cerulean City Gym Leader."
        },
        {
            "username": "brock_harrison",
            "email": "brock@pokemon.com",
            "display_name": "Brock",
            "password": "onix123",
            "bio": "Rock-type specialist and Pokemon breeder."
        }
    ]
    
    for user_data in demo_users:
        user_id = community_manager.register_user(**user_data)
        if user_id:
            print(f"  ✓ Created: {user_data['username']}")
        else:
            print(f"  ⚠ Skipped: {user_data['username']} (already exists)")
    
    # Create some sample tournaments
    print("\nCreating sample tournaments...")
    
    tournaments = [
        {
            "name": "Summer Championship 2024",
            "description": "Annual summer tournament featuring the best trainers!",
            "format": "OU (OverUsed)",
            "max_participants": 32
        },
        {
            "name": "Beginners Cup",
            "description": "Tournament for new trainers to test their skills.",
            "format": "Little Cup",
            "max_participants": 16
        }
    ]
    
    for tournament_data in tournaments:
        try:
            # Create tournament (using demo_user as organizer)
            if demo_user_id:
                tournament_id = community_manager.create_tournament(
                    organizer_id=demo_user_id,
                    **tournament_data
                )
                print(f"  ✓ Created: {tournament_data['name']}")
        except Exception as e:
            print(f"  ⚠ Error creating tournament: {e}")
    
    # Create some sample community posts
    print("\nCreating sample community posts...")
    
    from features.social_community_hub import PostType
    
    posts = [
        {
            "post_type": PostType.DISCUSSION,
            "title": "Welcome to the Pokemon Community!",
            "content": "Hello everyone! Welcome to our Pokemon Team Builder community. Share your teams, strategies, and connect with other trainers!",
            "tags": ["welcome", "introduction", "community"]
        },
        {
            "post_type": PostType.GUIDE,
            "title": "Guide: Building a Balanced Team",
            "content": "A balanced team should cover multiple types and roles. Here's a guide to building your first competitive team...",
            "tags": ["guide", "team-building", "competitive"]
        }
    ]
    
    if demo_user_id:
        for post_data in posts:
            try:
                post_id = community_manager.create_post(
                    user_id=demo_user_id,
                    **post_data
                )
                print(f"  ✓ Created: {post_data['title'][:50]}...")
            except Exception as e:
                print(f"  ⚠ Error creating post: {e}")
    
    print("\n" + "="*60)
    print("✓ Social database initialization complete!")
    print("="*60)
    print("\nYou can now use the Social Community Hub in the GUI.")
    print("\nLogin Credentials:")
    print("  Username: demo_user")
    print("  Password: demo123")
    print("\nOther demo accounts:")
    print("  ash_ketchum / pikachu123")
    print("  misty_waterflower / starmie123")
    print("  brock_harrison / onix123")
    print("="*60)


if __name__ == "__main__":
    main()
