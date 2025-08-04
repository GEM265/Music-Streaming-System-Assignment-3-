#!/usr/bin/env python3
"""
Music Streaming System - Design Patterns Implementation
Demonstrates: Singleton, Strategy, and Decorator patterns
"""

from abc import ABC, abstractmethod
from typing import List, Dict
import time
import threading

# ============================================================================
# SINGLETON PATTERN - Music Player (Creational)
# ============================================================================

class MusicPlayer:
    """
    Singleton Pattern Implementation for Music Player
    Ensures only one music player instance exists throughout the application
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MusicPlayer, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.current_song = None
        self.is_playing = False
        self.volume = 50
        self.playback_strategy = None
        print("🎵 Music Player initialized")
    
    def set_playback_strategy(self, strategy):
        """Set the audio format strategy"""
        self.playback_strategy = strategy
    
    def play(self, song):
        """Play a song using the current strategy"""
        if self.playback_strategy is None:
            print("❌ No playback strategy set!")
            return
        
        self.current_song = song
        self.is_playing = True
        self.playback_strategy.play(song)
    
    def pause(self):
        """Pause current playback"""
        if self.is_playing:
            self.is_playing = False
            print(f"⏸️  Paused: {self.current_song.title if self.current_song else 'Unknown'}")
        
    def stop(self):
        """Stop current playback"""
        self.is_playing = False
        self.current_song = None
        print("⏹️  Playback stopped")
    
    def set_volume(self, volume: int):
        """Set playback volume (0-100)"""
        self.volume = max(0, min(100, volume))
        print(f"🔊 Volume set to: {self.volume}")
    
    def get_status(self):
        """Get current player status"""
        status = "Playing" if self.is_playing else "Stopped"
        song_title = self.current_song.title if self.current_song else "None"
        return f"Status: {status} | Song: {song_title} | Volume: {self.volume}"

# ============================================================================
# STRATEGY PATTERN - Audio Format Playback (Behavioral)
# ============================================================================

class PlaybackStrategy(ABC):
    """
    Strategy Pattern Interface for different audio format playback
    Allows switching between different audio processing algorithms
    """
    
    @abstractmethod
    def play(self, song):
        pass
    
    @abstractmethod
    def get_format_info(self):
        pass

class MP3Strategy(PlaybackStrategy):
    """Strategy for MP3 audio format"""
    
    def play(self, song):
        print(f"🎵 Playing MP3: {song.title} by {song.artist}")
        print("   Using MP3 decoder with lossy compression")
        time.sleep(0.5)  # Simulate processing time
        
    def get_format_info(self):
        return "MP3: Lossy compression, smaller file size"

class FLACStrategy(PlaybackStrategy):
    """Strategy for FLAC audio format"""
    
    def play(self, song):
        print(f"🎵 Playing FLAC: {song.title} by {song.artist}")
        print("   Using FLAC decoder with lossless compression")
        time.sleep(1.0)  # Simulate longer processing time for high quality
        
    def get_format_info(self):
        return "FLAC: Lossless compression, high quality audio"

class StreamingStrategy(PlaybackStrategy):
    """Strategy for streaming audio"""
    
    def play(self, song):
        print(f"🎵 Streaming: {song.title} by {song.artist}")
        print("   Buffering... Loading adaptive bitrate stream")
        time.sleep(0.3)  # Simulate buffering
        
    def get_format_info(self):
        return "Streaming: Adaptive bitrate, network dependent"

# ============================================================================
# DECORATOR PATTERN - Enhanced Playlists (Structural)
# ============================================================================

class Song:
    """Basic song entity"""
    def __init__(self, title: str, artist: str, duration: int, format_type: str = "mp3"):
        self.title = title
        self.artist = artist
        self.duration = duration  # in seconds
        self.format_type = format_type
    
    def __str__(self):
        return f"{self.title} - {self.artist} ({self.duration}s)"

class Playlist(ABC):
    """
    Base Playlist interface for Decorator Pattern
    Allows adding functionality to playlists dynamically
    """
    
    @abstractmethod
    def add_song(self, song: Song):
        pass
    
    @abstractmethod
    def play_all(self):
        pass
    
    @abstractmethod
    def get_info(self):
        pass
    
    @abstractmethod
    def get_songs(self) -> List[Song]:
        pass

class BasicPlaylist(Playlist):
    """Basic playlist implementation"""
    
    def __init__(self, name: str):
        self.name = name
        self.songs: List[Song] = []
    
    def add_song(self, song: Song):
        self.songs.append(song)
        print(f"➕ Added '{song.title}' to playlist '{self.name}'")
    
    def play_all(self):
        print(f"▶️  Playing playlist: {self.name}")
        player = MusicPlayer()
        for song in self.songs:
            player.play(song)
            time.sleep(0.2)  # Brief pause between songs
    
    def get_info(self):
        total_duration = sum(song.duration for song in self.songs)
        return f"Playlist: {self.name} | Songs: {len(self.songs)} | Duration: {total_duration}s"
    
    def get_songs(self) -> List[Song]:
        return self.songs.copy()

class PlaylistDecorator(Playlist):
    """Base decorator for playlists"""
    
    def __init__(self, playlist: Playlist):
        self._playlist = playlist
    
    def add_song(self, song: Song):
        return self._playlist.add_song(song)
    
    def play_all(self):
        return self._playlist.play_all()
    
    def get_info(self):
        return self._playlist.get_info()
    
    def get_songs(self) -> List[Song]:
        return self._playlist.get_songs()

class ShuffleDecorator(PlaylistDecorator):
    """Decorator that adds shuffle functionality to playlists"""
    
    def __init__(self, playlist: Playlist):
        super().__init__(playlist)
        import random
        self.random = random
    
    def play_all(self):
        print("🔀 Shuffle mode enabled!")
        songs = self.get_songs()
        self.random.shuffle(songs)
        
        print(f"▶️  Playing shuffled playlist")
        player = MusicPlayer()
        for song in songs:
            player.play(song)
            time.sleep(0.2)
    
    def get_info(self):
        return self._playlist.get_info() + " | 🔀 Shuffle: ON"

class RepeatDecorator(PlaylistDecorator):
    """Decorator that adds repeat functionality to playlists"""
    
    def __init__(self, playlist: Playlist, repeat_count: int = 2):
        super().__init__(playlist)
        self.repeat_count = repeat_count
    
    def play_all(self):
        print(f"🔁 Repeat mode enabled! (x{self.repeat_count})")
        
        for i in range(self.repeat_count):
            print(f"▶️  Playing playlist - Round {i + 1}")
            self._playlist.play_all()
            if i < self.repeat_count - 1:
                print("   🔄 Repeating playlist...")
                time.sleep(0.3)
    
    def get_info(self):
        return self._playlist.get_info() + f" | 🔁 Repeat: {self.repeat_count}x"

class AnalyticsDecorator(PlaylistDecorator):
    """Decorator that adds analytics tracking to playlists"""
    
    def __init__(self, playlist: Playlist):
        super().__init__(playlist)
        self.play_count = 0
        self.total_listening_time = 0
    
    def play_all(self):
        print("📊 Analytics tracking enabled")
        start_time = time.time()
        
        self._playlist.play_all()
        
        self.play_count += 1
        duration = time.time() - start_time
        self.total_listening_time += duration
        print(f"📈 Session complete! Play count: {self.play_count}")
    
    def get_info(self):
        analytics = f" | 📊 Plays: {self.play_count}, Total time: {self.total_listening_time:.1f}s"
        return self._playlist.get_info() + analytics
    
    def get_analytics(self):
        """Get detailed analytics"""
        avg_session = self.total_listening_time / max(1, self.play_count)
        return {
            'play_count': self.play_count,
            'total_listening_time': round(self.total_listening_time, 1),
            'average_session_time': round(avg_session, 1)
        }

# ============================================================================
# DEMONSTRATION SYSTEM
# ============================================================================

class MusicStreamingSystem:
    """Main system that demonstrates all three design patterns"""
    
    def __init__(self):
        print("🎼 Initializing Music Streaming System...")
        print("=" * 50)
        
        # Initialize strategies
        self.strategies = {
            'mp3': MP3Strategy(),
            'flac': FLACStrategy(),
            'streaming': StreamingStrategy()
        }
        
        # Create sample songs
        self.songs = [
            Song("Bohemian Rhapsody", "Queen", 355, "flac"),
            Song("Stairway to Heaven", "Led Zeppelin", 482, "mp3"),
            Song("Hotel California", "Eagles", 391, "streaming"),
            Song("Sweet Child O' Mine", "Guns N' Roses", 356, "mp3"),
            Song("Imagine", "John Lennon", 183, "flac")
        ]
    
    def demonstrate_singleton(self):
        """Demonstrate Singleton pattern with multiple player instances"""
        print("\n🔍 DEMONSTRATING SINGLETON PATTERN")
        print("-" * 40)
        
        # Try to create multiple players
        player1 = MusicPlayer()
        player2 = MusicPlayer()
        player3 = MusicPlayer()
        
        print(f"Player 1 ID: {id(player1)}")
        print(f"Player 2 ID: {id(player2)}")
        print(f"Player 3 ID: {id(player3)}")
        print(f"All instances are the same: {player1 is player2 is player3}")
        
        # Demonstrate shared state
        player1.set_volume(75)
        print(f"Volume set by player1: {player1.volume}")
        print(f"Volume from player2: {player2.volume}")
        print(f"Volume from player3: {player3.volume}")
    
    def demonstrate_strategy(self):
        """Demonstrate Strategy pattern with different audio formats"""
        print("\n🔍 DEMONSTRATING STRATEGY PATTERN")
        print("-" * 40)
        
        player = MusicPlayer()
        
        for song in self.songs[:3]:  # Demo first 3 songs
            print(f"\n🎵 Processing: {song}")
            
            # Select appropriate strategy based on song format
            strategy = self.strategies.get(song.format_type, self.strategies['mp3'])
            print(f"📋 Strategy: {strategy.get_format_info()}")
            
            # Set strategy and play
            player.set_playback_strategy(strategy)
            player.play(song)
            time.sleep(0.5)
    
    def demonstrate_decorator(self):
        """Demonstrate Decorator pattern with enhanced playlists"""
        print("\n🔍 DEMONSTRATING DECORATOR PATTERN")
        print("-" * 40)
        
        # Create basic playlist
        basic_playlist = BasicPlaylist("Classic Rock Hits")
        for song in self.songs[:3]:
            basic_playlist.add_song(song)
        
        print(f"\n📋 Basic Playlist Info: {basic_playlist.get_info()}")
        
        # Add shuffle decorator
        shuffled_playlist = ShuffleDecorator(basic_playlist)
        print(f"📋 Shuffled Playlist Info: {shuffled_playlist.get_info()}")
        
        # Add repeat decorator to shuffled playlist
        repeat_shuffled = RepeatDecorator(shuffled_playlist, 2)
        print(f"📋 Repeat+Shuffle Info: {repeat_shuffled.get_info()}")
        
        # Add analytics decorator
        analytics_playlist = AnalyticsDecorator(repeat_shuffled)
        print(f"📋 Full Enhanced Playlist: {analytics_playlist.get_info()}")
        
        # Set up player for demo
        player = MusicPlayer()
        player.set_playback_strategy(self.strategies['mp3'])
        
        # Demonstrate enhanced playlist playback
        print("\n▶️  Playing enhanced playlist...")
        analytics_playlist.play_all()
        
        # Show analytics
        print(f"\n📊 Analytics: {analytics_playlist.get_analytics()}")
    
    def run_full_demo(self):
        """Run complete demonstration of all patterns"""
        print("🚀 Starting Complete Music Streaming System Demo")
        print("=" * 60)
        
        self.demonstrate_singleton()
        time.sleep(1)
        
        self.demonstrate_strategy()
        time.sleep(1)
        
        self.demonstrate_decorator()
        
        print("\n" + "=" * 60)
        print("✅ Demo Complete! All design patterns demonstrated.")
        
        # Final system status
        player = MusicPlayer()
        print(f"🎵 Final Player Status: {player.get_status()}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    system = MusicStreamingSystem()
    system.run_full_demo()
    
    # Interactive mode
    print("\n" + "=" * 50)
    print("🎮 Interactive Mode - Try the system!")
    print("=" * 50)
    
    player = MusicPlayer()
    player.set_playback_strategy(MP3Strategy())
    
    # Create a sample interactive playlist
    my_playlist = BasicPlaylist("My Favorites")
    my_playlist.add_song(Song("Test Song 1", "Test Artist", 180))
    my_playlist.add_song(Song("Test Song 2", "Another Artist", 200))
    
    # Enhance with decorators
    enhanced_playlist = AnalyticsDecorator(
        ShuffleDecorator(my_playlist)
    )
    
    print(f"📋 Your playlist: {enhanced_playlist.get_info()}")
    print("▶️  Playing your enhanced playlist...")
    enhanced_playlist.play_all()
    
    print(f"📊 Final analytics: {enhanced_playlist.get_analytics()}")

if __name__ == "__main__":
    main()