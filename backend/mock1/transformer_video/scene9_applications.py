from manim import *
from utils import TransformerBaseScene
import numpy as np

class ApplicationsScene(TransformerBaseScene):
    """Ninth scene: Applications & Takeaway of Transformers."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Create a background
        background = self.create_gradient_background()
        
        # Create a simplified transformer model representation
        transformer_width = 5
        transformer_height = 6
        
        transformer = Rectangle(
            width=transformer_width,
            height=transformer_height,
            fill_color=self.color_palette["embedding"],
            fill_opacity=0.2,
            stroke_color=WHITE,
            stroke_width=2
        )
        transformer.move_to(ORIGIN)
        
        # Add internal structure to the transformer (simplified)
        encoder_part = Rectangle(
            width=transformer_width - 0.5,
            height=transformer_height/2 - 0.5,
            fill_color=self.color_palette["embedding"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        encoder_part.move_to(transformer.get_top() + DOWN * transformer_height/4)
        
        encoder_label = Text("Encoder", font_size=24)
        encoder_label.move_to(encoder_part)
        
        decoder_part = Rectangle(
            width=transformer_width - 0.5,
            height=transformer_height/2 - 0.5,
            fill_color=self.color_palette["value"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        decoder_part.move_to(transformer.get_bottom() + UP * transformer_height/4)
        
        decoder_label = Text("Decoder", font_size=24)
        decoder_label.move_to(decoder_part)
        
        attention_block = Rectangle(
            width=3,
            height=1,
            fill_color=self.color_palette["attention"],
            fill_opacity=0.5,
            stroke_color=WHITE,
            stroke_width=1
        )
        attention_block.move_to(ORIGIN)
        
        attention_label = Text("Attention", font_size=20)
        attention_label.move_to(attention_block)
        
        model_group = VGroup(
            transformer, encoder_part, encoder_label,
            decoder_part, decoder_label,
            attention_block, attention_label
        )
        
        # Create icons for applications
        icon_size = 1.2
        
        # Translation icon
        translation_icon = VGroup()
        lang1 = Text("EN", font_size=24)
        lang2 = Text("FR", font_size=24)
        arrow = Arrow(LEFT, RIGHT, buff=0.1)
        lang1.next_to(arrow, LEFT, buff=0.2)
        lang2.next_to(arrow, RIGHT, buff=0.2)
        translation_icon.add(lang1, arrow, lang2)
        
        # Circular background for translation
        translation_circle = Circle(
            radius=icon_size,
            fill_color=self.color_palette["query"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        translation_circle.move_to(LEFT * 4 + UP * 2)
        translation_icon.move_to(translation_circle.get_center())
        
        translation_label = Text("Translation", font_size=20)
        translation_label.next_to(translation_circle, DOWN, buff=0.3)
        
        translation_group = VGroup(translation_circle, translation_icon, translation_label)
        
        # Summarization icon
        summarization_icon = VGroup()
        doc = Rectangle(height=0.8, width=0.6, stroke_width=1)
        lines = VGroup()
        for i in range(3):
            line = Line(LEFT * 0.25, RIGHT * 0.25, stroke_width=1)
            line.move_to(doc.get_top() + DOWN * (0.2 + i * 0.2))
            lines.add(line)
        doc_small = Rectangle(height=0.4, width=0.6, stroke_width=1)
        doc_small.next_to(doc, RIGHT, buff=0.6)
        summarization_icon.add(doc, lines, doc_small)
        
        # Circular background for summarization
        summarization_circle = Circle(
            radius=icon_size,
            fill_color=self.color_palette["key"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        summarization_circle.move_to(RIGHT * 4 + UP * 2)
        summarization_icon.move_to(summarization_circle.get_center())
        
        summarization_label = Text("Summarization", font_size=20)
        summarization_label.next_to(summarization_circle, DOWN, buff=0.3)
        
        summarization_group = VGroup(summarization_circle, summarization_icon, summarization_label)
        
        # Question answering icon
        qa_icon = VGroup()
        question = Text("?", font_size=48)
        answer = Text("!", font_size=48)
        qa_icon.add(question, answer)
        question.shift(LEFT * 0.3)
        answer.shift(RIGHT * 0.3)
        
        # Circular background for QA
        qa_circle = Circle(
            radius=icon_size,
            fill_color=self.color_palette["value"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        qa_circle.move_to(LEFT * 4 + DOWN * 2)
        qa_icon.move_to(qa_circle.get_center())
        
        qa_label = Text("Question Answering", font_size=20)
        qa_label.next_to(qa_circle, DOWN, buff=0.3)
        
        qa_group = VGroup(qa_circle, qa_icon, qa_label)
        
        # Chatbot icon
        chatbot_icon = VGroup()
        bubble1 = Bubble(height=0.6, width=0.8)
        bubble2 = Bubble(height=0.6, width=0.8, direction=RIGHT)
        bubble1.shift(LEFT * 0.2 + UP * 0.2)
        bubble2.shift(RIGHT * 0.2 + DOWN * 0.2)
        chatbot_icon.add(bubble1, bubble2)
        
        # Circular background for chatbot
        chatbot_circle = Circle(
            radius=icon_size,
            fill_color=self.color_palette["embedding"],
            fill_opacity=0.3,
            stroke_color=WHITE,
            stroke_width=1.5
        )
        chatbot_circle.move_to(RIGHT * 4 + DOWN * 2)
        chatbot_icon.move_to(chatbot_circle.get_center())
        
        chatbot_label = Text("Chatbots", font_size=20)
        chatbot_label.next_to(chatbot_circle, DOWN, buff=0.3)
        
        chatbot_group = VGroup(chatbot_circle, chatbot_icon, chatbot_label)
        
        # Create a final title
        final_title = Text("Transformers: The Foundation of Modern NLP", font_size=48)
        final_title.to_edge(UP, buff=0.5)
        
        # Animation sequence
        with self.voiceover(
            """From machine translation to chatbots and beyond, Transformers have revolutionized 
            NLP and vision alike. All thanks to the simple yet powerful mechanism of attention."""
        ):
            # Add background
            self.add(background)
            
            # Show the transformer model in the center
            self.play(
                FadeIn(transformer),
                run_time=1
            )
            
            # Show the internal structure
            self.play(
                FadeIn(encoder_part),
                Write(encoder_label),
                FadeIn(decoder_part),
                Write(decoder_label),
                run_time=1
            )
            
            # Highlight the attention mechanism
            self.play(
                FadeIn(attention_block),
                Write(attention_label),
                run_time=1
            )
            
            # Show the application areas one by one
            
            # Translation
            self.play(
                FadeIn(translation_circle),
                run_time=0.5
            )
            
            self.play(
                FadeIn(translation_icon),
                Write(translation_label),
                run_time=0.8
            )
            
            # Connect to the transformer with an arrow
            translation_arrow = Arrow(
                translation_circle.get_right(),
                transformer.get_left() + UP * 1,
                buff=0.1,
                color=self.color_palette["query"]
            )
            
            self.play(
                GrowArrow(translation_arrow),
                run_time=0.6
            )
            
            # Pulse animation for translation
            self.play(
                translation_circle.animate.scale(1.1),
                run_time=0.3
            )
            
            self.play(
                translation_circle.animate.scale(1/1.1),
                run_time=0.3
            )
            
            # Summarization
            self.play(
                FadeIn(summarization_circle),
                run_time=0.5
            )
            
            self.play(
                FadeIn(summarization_icon),
                Write(summarization_label),
                run_time=0.8
            )
            
            # Connect to the transformer with an arrow
            summarization_arrow = Arrow(
                summarization_circle.get_left(),
                transformer.get_right() + UP * 1,
                buff=0.1,
                color=self.color_palette["key"]
            )
            
            self.play(
                GrowArrow(summarization_arrow),
                run_time=0.6
            )
            
            # Pulse animation for summarization
            self.play(
                summarization_circle.animate.scale(1.1),
                run_time=0.3
            )
            
            self.play(
                summarization_circle.animate.scale(1/1.1),
                run_time=0.3
            )
            
            # Question Answering
            self.play(
                FadeIn(qa_circle),
                run_time=0.5
            )
            
            self.play(
                FadeIn(qa_icon),
                Write(qa_label),
                run_time=0.8
            )
            
            # Connect to the transformer with an arrow
            qa_arrow = Arrow(
                qa_circle.get_right(),
                transformer.get_left() + DOWN * 1,
                buff=0.1,
                color=self.color_palette["value"]
            )
            
            self.play(
                GrowArrow(qa_arrow),
                run_time=0.6
            )
            
            # Pulse animation for QA
            self.play(
                qa_circle.animate.scale(1.1),
                run_time=0.3
            )
            
            self.play(
                qa_circle.animate.scale(1/1.1),
                run_time=0.3
            )
            
            # Chatbots
            self.play(
                FadeIn(chatbot_circle),
                run_time=0.5
            )
            
            self.play(
                FadeIn(chatbot_icon),
                Write(chatbot_label),
                run_time=0.8
            )
            
            # Connect to the transformer with an arrow
            chatbot_arrow = Arrow(
                chatbot_circle.get_left(),
                transformer.get_right() + DOWN * 1,
                buff=0.1,
                color=self.color_palette["embedding"]
            )
            
            self.play(
                GrowArrow(chatbot_arrow),
                run_time=0.6
            )
            
            # Pulse animation for chatbots
            self.play(
                chatbot_circle.animate.scale(1.1),
                run_time=0.3
            )
            
            self.play(
                chatbot_circle.animate.scale(1/1.1),
                run_time=0.3
            )
            
            # Show the final title
            self.play(
                Write(final_title),
                run_time=1.5
            )
            
            # Final animation - make the whole transformer glow
            glow_effect = transformer.copy()
            glow_effect.set_stroke(self.color_palette["highlight"], width=8, opacity=0.8)
            
            self.play(
                Create(glow_effect),
                run_time=1
            )
            
            self.play(
                FadeOut(glow_effect),
                run_time=1
            )
            
            self.wait(1) 