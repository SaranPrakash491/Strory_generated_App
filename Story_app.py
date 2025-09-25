import streamlit as st
import random
import json
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Tuple
import base64
import io
from collections import Counter
import re

# Page configuration
st.set_page_config(
    page_title="AI Mood-to-Story Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        animation: gradient 3s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .mood-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .mood-card:hover {
        transform: translateY(-5px);
    }
    .story-card {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border-left: 6px solid #FF6B6B;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .character-card {
        background: linear-gradient(135deg, #96CEB4 0%, #4ECDC4 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .emotion-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


class MoodToStoryGenerator:
    def __init__(self):
        self.moods = {
            "Joyful": {"emoji": "😊", "colors": ["#FFD93D", "#6BCF7F"], "genre": "Adventure/Comedy"},
            "Melancholic": {"emoji": "😔", "colors": ["#95B8D1", "#6C5B7B"], "genre": "Drama/Reflective"},
            "Mysterious": {"emoji": "🕵️", "colors": ["#2D3047", "#419D78"], "genre": "Mystery/Thriller"},
            "Romantic": {"emoji": "❤️", "colors": ["#FF6B6B", "#FFA5A5"], "genre": "Romance/Drama"},
            "Adventurous": {"emoji": "🏔️", "colors": ["#355070", "#6D597A"], "genre": "Action/Adventure"},
            "Whimsical": {"emoji": "🌈", "colors": ["#9B5DE5", "#F15BB5"], "genre": "Fantasy/Fairy Tale"},
            "Horror": {"emoji": "👻", "colors": ["#2D1B2E", "#8B1E3F"], "genre": "Horror/Suspense"},
            "Nostalgic": {"emoji": "📻", "colors": ["#8F754F", "#D4B483"], "genre": "Historical/Memoir"}
        }

        self.story_elements = {
            "characters": ["detective", "artist", "scientist", "traveler", "student", "warrior", "dreamer", "explorer"],
            "settings": ["ancient forest", "futuristic city", "seaside village", "mountain monastery", "desert oasis",
                         "underground library"],
            "conflicts": ["lost treasure", "forbidden love", "ancient prophecy", "technological revolution",
                          "family secret", "cosmic mystery"]
        }

        self.writing_styles = [
            "Descriptive", "Dialogue-heavy", "Poetic", "Fast-paced", "Reflective", "Suspenseful"
        ]

    def analyze_mood_text(self, text: str) -> Dict:
        """Analyze text input to detect mood"""
        mood_keywords = {
            "Joyful": ["happy", "excited", "wonderful", "amazing", "beautiful", "love", "fantastic"],
            "Melancholic": ["sad", "lonely", "miss", "lost", "empty", "regret", "memory"],
            "Mysterious": ["secret", "mystery", "unknown", "hidden", "curious", "strange"],
            "Romantic": ["love", "heart", "romance", "passion", "kiss", "darling", "sweet"],
            "Adventurous": ["adventure", "explore", "journey", "discover", "risk", "brave"],
            "Whimsical": ["magic", "dream", "fantasy", "imagine", "wonder", "magical"],
            "Horror": ["scary", "fear", "dark", "terror", "ghost", "haunted"],
            "Nostalgic": ["remember", "past", "childhood", "old", "memory", "traditional"]
        }

        text_lower = text.lower()
        mood_scores = {mood: 0 for mood in self.moods}

        for mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mood_scores[mood] += text_lower.count(keyword) * 2

        # Detect emotional intensity
        intensity_indicators = ["very", "extremely", "really", "so", "absolutely"]
        intensity = 1
        for indicator in intensity_indicators:
            if indicator in text_lower:
                intensity += 0.5

        dominant_mood = max(mood_scores, key=mood_scores.get)
        return {
            "dominant_mood": dominant_mood if mood_scores[dominant_mood] > 0 else "Joyful",
            "mood_scores": mood_scores,
            "intensity": min(intensity, 3),
            "word_count": len(text.split())
        }

    def generate_story(self, mood: str, user_input: str = "", style: str = "Descriptive",
                       length: str = "Medium") -> Dict:
        """Generate story based on mood and parameters"""

        # Story templates based on mood
        story_templates = {
            "Joyful": [
                "In a world filled with laughter, {character} discovered {element} that brought joy to everyone around.",
                "The sun shone brightly as {character} embarked on a delightful journey to {setting}."
            ],
            "Melancholic": [
                "As the rain fell softly, {character} remembered the days when {setting} was filled with life and laughter.",
                "In the quiet emptiness of {setting}, {character} contemplated the meaning of {element}."
            ],
            "Mysterious": [
                "When {character} found the ancient {element} in {setting}, little did they know it would unravel a centuries-old secret.",
                "The mysterious events in {setting} led {character} on a quest to uncover the truth about {element}."
            ],
            "Romantic": [
                "Under the starlit sky of {setting}, {character} found love in the most unexpected place while searching for {element}.",
                "The story of {character}'s heart began in {setting}, where {element} brought two souls together."
            ],
            "Adventurous": [
                "With courage in heart, {character} ventured into {setting} to discover the legendary {element}.",
                "The perilous journey through {setting} tested {character}'s resolve to secure {element}."
            ],
            "Whimsical": [
                "In a land where dreams came alive, {character} discovered that {setting} held the magical {element}.",
                "Through the rainbow portal, {character} entered {setting} where {element} awaited with wonder."
            ],
            "Horror": [
                "The shadows in {setting} whispered secrets that {character} wished they never uncovered about {element}.",
                "When {character} found the cursed {element} in {setting}, the nightmare began."
            ],
            "Nostalgic": [
                "Returning to {setting} after years, {character} rediscovered {element} that brought back cherished memories.",
                "The old photograph led {character} back to {setting}, where the story of {element} unfolded."
            ]
        }

        # Generate story elements
        character = random.choice(self.story_elements["characters"])
        setting = random.choice(self.story_elements["settings"])
        conflict = random.choice(self.story_elements["conflicts"])

        # Select template and generate story
        template = random.choice(story_templates[mood])
        story_seed = template.format(character=character, setting=setting, element=conflict)

        # Expand based on length
        length_words = {"Short": 100, "Medium": 300, "Long": 600}
        target_words = length_words[length]

        # Generate full story (simulated AI generation)
        story = self._expand_story(story_seed, mood, style, target_words)

        return {
            "title": f"The {mood} {conflict.replace(' ', ' ')}",
            "story": story,
            "mood": mood,
            "character": character,
            "setting": setting,
            "conflict": conflict,
            "style": style,
            "length": len(story.split()),
            "emotional_arc": self._generate_emotional_arc(mood),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _expand_story(self, seed: str, mood: str, style: str, target_words: int) -> str:
        """Expand story seed to target length"""
        # This would be replaced with actual AI model in production
        story_expansions = {
            "Joyful": "The air was filled with the scent of blooming flowers as birds sang cheerful melodies. Every step brought new discoveries and happy encounters with friendly creatures who shared their wisdom and laughter.",
            "Melancholic": "The gentle breeze carried memories of times long past, each whisper echoing through the empty spaces where joy once resided. Time moved slowly, as if respecting the weight of the moments being remembered.",
            "Mysterious": "Shadows danced in the corners, hiding secrets that begged to be uncovered. Every clue led to deeper questions, and the truth seemed to shift with each passing moment.",
            "Romantic": "Hearts beat in synchrony as fate wove its invisible threads between souls destined to meet. Every glance held unspoken promises, and every touch sparked constellations of emotion.",
            "Adventurous": "Danger lurked around every corner, but so did opportunity. The path ahead was uncertain, but the call of discovery was stronger than any fear that tried to hold back progress.",
            "Whimsical": "Reality bent in delightful ways, where impossible things became ordinary and magic was as common as sunlight. The rules of physics took a holiday, allowing wonder to reign supreme.",
            "Horror": "Silence screamed louder than any sound, and the darkness seemed to breathe with malicious intent. Every shadow held potential threats, and trust became a dangerous luxury.",
            "Nostalgic": "The past reached through time with gentle hands, reminding of lessons learned and loves lost. Each memory was a treasure, carefully preserved in the museum of the heart."
        }

        base_story = seed + " " + story_expansions.get(mood, "")
        words = base_story.split()

        # Expand to target length
        while len(words) < target_words:
            expansion = " ".join(random.sample(words, min(10, len(words))))
            words.extend(expansion.split())

        return " ".join(words[:target_words])

    def _generate_emotional_arc(self, mood: str) -> List[Dict]:
        """Generate emotional arc for the story"""
        arcs = {
            "Joyful": [("Beginning", 0.7), ("Rising", 0.9), ("Climax", 1.0), ("Resolution", 0.8)],
            "Melancholic": [("Beginning", 0.3), ("Rising", 0.5), ("Climax", 0.8), ("Resolution", 0.4)],
            "Mysterious": [("Beginning", 0.4), ("Rising", 0.7), ("Climax", 0.9), ("Resolution", 0.6)],
            "Romantic": [("Beginning", 0.6), ("Rising", 0.8), ("Climax", 0.95), ("Resolution", 0.85)],
            "Adventurous": [("Beginning", 0.5), ("Rising", 0.8), ("Climax", 0.9), ("Resolution", 0.7)],
            "Whimsical": [("Beginning", 0.8), ("Rising", 0.9), ("Climax", 0.95), ("Resolution", 0.85)],
            "Horror": [("Beginning", 0.3), ("Rising", 0.6), ("Climax", 0.2), ("Resolution", 0.5)],
            "Nostalgic": [("Beginning", 0.4), ("Rising", 0.7), ("Climax", 0.8), ("Resolution", 0.6)]
        }

        return [{"stage": stage, "intensity": intensity} for stage, intensity in arcs.get(mood, arcs["Joyful"])]


def main():
    # Initialize generator
    generator = MoodToStoryGenerator()

    # Header
    st.markdown('<div class="main-header">📖 AI Mood-to-Story Generator</div>', unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title("🎛️ Controls")
    app_mode = st.sidebar.radio("Select Mode",
                                ["Mood Analysis", "Story Generation", "Story Library", "Writing Assistant"])

    # Main content
    if app_mode == "Mood Analysis":
        show_mood_analysis(generator)
    elif app_mode == "Story Generation":
        show_story_generation(generator)
    elif app_mode == "Story Library":
        show_story_library(generator)
    elif app_mode == "Writing Assistant":
        show_writing_assistant(generator)


def show_mood_analysis(generator):
    st.header("😊 Mood Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Describe Your Mood")
        user_text = st.text_area(
            "Share your feelings, thoughts, or current mood:",
            placeholder="I'm feeling excited about the future and curious about what adventures await...",
            height=150
        )

        if st.button("Analyze Mood", use_container_width=True):
            if user_text.strip():
                with st.spinner("Analyzing your mood..."):
                    time.sleep(2)
                    analysis = generator.analyze_mood_text(user_text)

                    # Display results
                    mood_info = generator.moods[analysis["dominant_mood"]]

                    st.markdown(f"""
                    <div class="mood-card">
                        <h2>{mood_info['emoji']} {analysis['dominant_mood']} Mood Detected</h2>
                        <p>Genre: {mood_info['genre']}</p>
                        <p>Intensity: {'⭐' * int(analysis['intensity'])}</p>
                        <p>Word Count: {analysis['word_count']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Mood scores visualization
                    scores_df = pd.DataFrame({
                        'Mood': list(analysis['mood_scores'].keys()),
                        'Score': list(analysis['mood_scores'].values())
                    })
                    scores_df = scores_df[scores_df['Score'] > 0]

                    if not scores_df.empty:
                        fig = px.bar(scores_df, x='Mood', y='Score',
                                     title="Mood Analysis Scores",
                                     color='Score', color_continuous_scale='Viridis')
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Please enter some text to analyze your mood.")

    with col2:
        st.subheader("Mood Palette")
        for mood, info in generator.moods.items():
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {info['colors'][0]}, {info['colors'][1]}); 
                        padding: 0.5rem; border-radius: 10px; margin: 0.5rem 0; color: white; text-align: center;">
                {info['emoji']} {mood}
            </div>
            """, unsafe_allow_html=True)


def show_story_generation(generator):
    st.header("✨ Story Generation")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Story Parameters")

        # Mood selection
        selected_mood = st.selectbox(
            "Choose Story Mood",
            list(generator.moods.keys()),
            format_func=lambda x: f"{generator.moods[x]['emoji']} {x}"
        )

        # Writing style
        writing_style = st.selectbox("Writing Style", generator.writing_styles)

        # Story length
        story_length = st.radio("Story Length", ["Short", "Medium", "Long"])

        # Additional inputs
        custom_character = st.text_input("Custom Character (optional)")
        custom_setting = st.text_input("Custom Setting (optional)")

        # Advanced options
        with st.expander("Advanced Options"):
            emotional_arc = st.slider("Emotional Intensity", 1, 10, 7)
            include_twist = st.checkbox("Include Plot Twist")
            target_audience = st.selectbox("Target Audience", ["Children", "Young Adult", "Adult", "All Ages"])

    with col2:
        st.subheader("Generate Your Story")

        if st.button("🎭 Generate Story", use_container_width=True):
            with st.spinner("Crafting your unique story..."):
                time.sleep(3)

                # Generate story
                story_data = generator.generate_story(
                    mood=selected_mood,
                    style=writing_style,
                    length=story_length
                )

                # Store story in session state
                if 'stories' not in st.session_state:
                    st.session_state.stories = []
                st.session_state.stories.append(story_data)

                # Display story
                mood_info = generator.moods[selected_mood]

                st.markdown(f"""
                <div class="story-card">
                    <h2 style="color: {mood_info['colors'][0]};">{story_data['title']}</h2>
                    <p><strong>Mood:</strong> {mood_info['emoji']} {selected_mood}</p>
                    <p><strong>Style:</strong> {writing_style}</p>
                    <p><strong>Length:</strong> {story_data['length']} words</p>
                    <hr>
                    {story_data['story']}
                </div>
                """, unsafe_allow_html=True)

                # Emotional arc visualization
                st.subheader("📈 Emotional Arc")
                arc_df = pd.DataFrame(story_data['emotional_arc'])
                fig = px.line(arc_df, x='stage', y='intensity',
                              title="Story Emotional Journey",
                              markers=True, line_shape='spline')
                st.plotly_chart(fig, use_container_width=True)


def show_story_library(generator):
    st.header("📚 Story Library")

    if 'stories' not in st.session_state or not st.session_state.stories:
        st.info("No stories generated yet. Go to 'Story Generation' to create your first story!")
        return

    # Display all generated stories
    for i, story in enumerate(reversed(st.session_state.stories)):
        with st.expander(f"{i + 1}. {story['title']} - {story['generated_at']}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(story['story'])

            with col2:
                mood_info = generator.moods[story['mood']]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {mood_info['colors'][0]}, {mood_info['colors'][1]});
                            padding: 1rem; border-radius: 10px; color: white;">
                    <p><strong>Mood:</strong> {story['mood']}</p>
                    <p><strong>Style:</strong> {story['style']}</p>
                    <p><strong>Words:</strong> {story['length']}</p>
                    <p><strong>Character:</strong> {story['character']}</p>
                    <p><strong>Setting:</strong> {story['setting']}</p>
                </div>
                """, unsafe_allow_html=True)

                # Export options
                if st.button(f"Export Story {i + 1}", key=f"export_{i}"):
                    create_download_link(story, f"story_{i + 1}.txt")


def show_writing_assistant(generator):
    st.header("✍️ Writing Assistant")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Story Enhancer")
        story_to_enhance = st.text_area("Paste your story for enhancement:", height=200)

        if st.button("Enhance Story"):
            if story_to_enhance:
                with st.spinner("Enhancing your story..."):
                    time.sleep(2)
                    # Simulate enhancement
                    enhanced_story = story_to_enhance + "\n\n[Enhanced with richer descriptions and emotional depth]"
                    st.text_area("Enhanced Story", enhanced_story, height=200)
            else:
                st.warning("Please enter a story to enhance")

    with col2:
        st.subheader("Writing Prompts")
        selected_mood = st.selectbox("Prompt Mood", list(generator.moods.keys()))

        if st.button("Generate Writing Prompt"):
            prompt = f"Write a {selected_mood.lower()} story about a {random.choice(generator.story_elements['characters'])} " \
                     f"in {random.choice(generator.story_elements['settings'])} " \
                     f"who discovers {random.choice(generator.story_elements['conflicts'])}."

            st.info(f"**Prompt:** {prompt}")

        st.subheader("Word Count Analysis")
        text_to_analyze = st.text_area("Text to analyze:", height=100)
        if text_to_analyze:
            words = len(text_to_analyze.split())
            sentences = len(re.findall(r'[.!?]+', text_to_analyze))
            st.metric("Word Count", words)
            st.metric("Sentences", sentences)


def create_download_link(story_data, filename):
    """Create download link for story"""
    story_text = f"Title: {story_data['title']}\n\n{story_data['story']}\n\nGenerated: {story_data['generated_at']}"
    b64 = base64.b64encode(story_text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">Download Story</a>'
    st.markdown(href, unsafe_allow_html=True)


# Future enhancements section
def show_future_enhancements():
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Future Features")
    st.sidebar.info("""
    Coming Soon:
    - AI Model Integration (GPT, Claude)
    - Voice Narration
    - Collaborative Storytelling
    - Image Generation
    - Multi-language Support
    - Story Series Creation
    - Character Development Tools
    - Plot Structure Analysis
    - Real-time Co-writing
    - Mobile App Version
    """)


if __name__ == "__main__":
    main()
    show_future_enhancements()