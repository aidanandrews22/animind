from manim import *
from utils import TransformerBaseScene
import numpy as np

class StackingDecoderScene(TransformerBaseScene):
    """Eighth scene: Stacking Encoder Layers and Decoder Preview."""
    
    def construct(self):
        # Set up voice
        self.set_speech_service(self.gtts_service)
        
        # Define the components for stacked encoder layers
        num_layers = 6
        
        # Create encoder layer blocks (simplified representation)
        encoder_layers = []
        encoder_labels = []
        
        layer_width = 5
        layer_height = 0.8
        
        # Create encoder layers
        for i in range(num_layers):
            layer = Rectangle(
                width=layer_width,
                height=layer_height,
                fill_color=self.color_palette["embedding"],
                fill_opacity=0.3,
                stroke_color=WHITE,
                stroke_width=2
            )
            
            if i == 0:
                layer.to_edge(LEFT, buff=2).shift(UP * 2)
            else:
                layer.next_to(encoder_layers[i-1], DOWN, buff=0.3)
            
            label = Text(f"Encoder Layer {i+1}", font_size=24)
            label.next_to(layer, LEFT, buff=0.3)
            
            encoder_layers.append(layer)
            encoder_labels.append(label)
        
        # Group all encoder elements
        encoder_stack = VGroup(*encoder_layers, *encoder_labels)
        
        # Create connections between encoder layers
        encoder_arrows = []
        for i in range(num_layers-1):
            arrow = Arrow(
                encoder_layers[i].get_bottom(),
                encoder_layers[i+1].get_top(),
                buff=0.1
            )
            encoder_arrows.append(arrow)
        
        # Create decoder layer blocks (simplified representation)
        decoder_layers = []
        decoder_labels = []
        
        # Create decoder layers
        for i in range(num_layers):
            layer = Rectangle(
                width=layer_width,
                height=layer_height,
                fill_color=self.color_palette["value"],
                fill_opacity=0.3,
                stroke_color=WHITE,
                stroke_width=2
            )
            
            if i == 0:
                layer.next_to(encoder_layers[0], RIGHT, buff=4)
            else:
                layer.next_to(decoder_layers[i-1], DOWN, buff=0.3)
            
            label = Text(f"Decoder Layer {i+1}", font_size=24)
            label.next_to(layer, RIGHT, buff=0.3)
            
            decoder_layers.append(layer)
            decoder_labels.append(label)
        
        # Group all decoder elements
        decoder_stack = VGroup(*decoder_layers, *decoder_labels)
        
        # Create connections between decoder layers
        decoder_arrows = []
        for i in range(num_layers-1):
            arrow = Arrow(
                decoder_layers[i].get_bottom(),
                decoder_layers[i+1].get_top(),
                buff=0.1
            )
            decoder_arrows.append(arrow)
        
        # Create cross-attention arrows from encoder to decoder
        cross_arrows = []
        for i in range(num_layers):
            arrow = Arrow(
                encoder_layers[i].get_right(),
                decoder_layers[i].get_left(),
                buff=0.1,
                color=self.color_palette["attention"]
            )
            cross_arrows.append(arrow)
        
        # Create input and output labels
        encoder_input = Text("Input Sequence", font_size=24)
        encoder_input.next_to(encoder_layers[0], UP, buff=0.5)
        
        encoder_output = Text("Encoder Output", font_size=24)
        encoder_output.next_to(encoder_layers[-1], DOWN, buff=0.5)
        
        decoder_input = Text("Output Sequence\n(shifted right)", font_size=24)
        decoder_input.next_to(decoder_layers[0], UP, buff=0.5)
        
        decoder_output = Text("Decoder Output", font_size=24)
        decoder_output.next_to(decoder_layers[-1], DOWN, buff=0.5)
        
        # Create annotations for decoder-specific components
        masked_attn_label = Text("Masked\nSelf-Attention", font_size=20, color=self.color_palette["key"])
        masked_attn_label.next_to(decoder_layers[1], LEFT, buff=1.8)
        
        cross_attn_label = Text("Cross-Attention", font_size=20, color=self.color_palette["attention"])
        cross_attn_label.next_to(decoder_layers[3], LEFT, buff=1.8)
        
        # Animation sequence
        with self.voiceover(
            """Transformers cascade multiple encoder layers to build deep contextual representations. 
            Decoders mirror this structure, adding a second attention step to look back at encoder 
            outputs—crucial for sequence generation."""
        ):
            # Show encoder stack
            for i, (layer, label) in enumerate(zip(encoder_layers, encoder_labels)):
                self.play(
                    FadeIn(layer),
                    Write(label),
                    run_time=0.5 if i > 0 else 1  # First layer shown more slowly
                )
                
                if i < num_layers-1:
                    self.play(GrowArrow(encoder_arrows[i]), run_time=0.3)
            
            # Show input/output labels for encoder
            self.play(
                Write(encoder_input),
                Write(encoder_output)
            )
            
            # Highlight encoder stack
            encoder_highlight = SurroundingRectangle(
                VGroup(*encoder_layers),
                color=self.color_palette["embedding"],
                buff=0.2
            )
            
            self.play(Create(encoder_highlight))
            self.wait(0.5)
            
            # Start revealing decoder (partially)
            for i, (layer, label) in enumerate(zip(decoder_layers[:2], decoder_labels[:2])):
                self.play(
                    FadeIn(layer),
                    Write(label),
                    run_time=0.8
                )
                
                if i < 1:
                    self.play(GrowArrow(decoder_arrows[i]), run_time=0.3)
            
            # Show the masked self-attention annotation
            masked_attn_arrow = Arrow(
                masked_attn_label.get_right(),
                decoder_layers[1].get_left() + UP * 0.2,
                buff=0.1,
                color=self.color_palette["key"]
            )
            
            self.play(
                Write(masked_attn_label),
                GrowArrow(masked_attn_arrow)
            )
            
            # Continue with more decoder layers
            for i in range(2, 4):
                self.play(
                    FadeIn(decoder_layers[i]),
                    Write(decoder_labels[i]),
                    run_time=0.5
                )
                
                self.play(GrowArrow(decoder_arrows[i-1]), run_time=0.3)
            
            # Show cross-attention connection for a visible decoder layer
            self.play(GrowArrow(cross_arrows[3]), run_time=0.8)
            
            # Show the cross-attention annotation
            cross_attn_arrow = Arrow(
                cross_attn_label.get_right(),
                decoder_layers[3].get_left() + DOWN * 0.2,
                buff=0.1,
                color=self.color_palette["attention"]
            )
            
            self.play(
                Write(cross_attn_label),
                GrowArrow(cross_attn_arrow)
            )
            
            # Complete the decoder stack (quickly)
            for i in range(4, num_layers):
                self.play(
                    FadeIn(decoder_layers[i]),
                    Write(decoder_labels[i]),
                    run_time=0.4
                )
                
                if i < num_layers-1:
                    self.play(GrowArrow(decoder_arrows[i-1]), run_time=0.2)
            
            # Show remaining cross-connections (quickly)
            remaining_cross = [cross_arrows[i] for i in [0, 1, 2, 4, 5]]
            self.play(*[GrowArrow(arrow) for arrow in remaining_cross], run_time=1)
            
            # Show decoder input/output
            self.play(
                Write(decoder_input),
                Write(decoder_output)
            )
            
            # Highlight decoder stack
            decoder_highlight = SurroundingRectangle(
                VGroup(*decoder_layers),
                color=self.color_palette["value"],
                buff=0.2
            )
            
            self.play(Create(decoder_highlight))
            
            # Highlight the overall Transformer architecture
            full_transformer = VGroup(
                encoder_stack, decoder_stack,
                *encoder_arrows, *decoder_arrows, *cross_arrows,
                encoder_input, encoder_output,
                decoder_input, decoder_output
            )
            
            transformer_title = Text("Complete Transformer Architecture", font_size=36, color=self.color_palette["text"])
            transformer_title.to_edge(UP, buff=0.2)
            
            self.play(
                Write(transformer_title),
                run_time=1
            )
            
            self.wait(1) 