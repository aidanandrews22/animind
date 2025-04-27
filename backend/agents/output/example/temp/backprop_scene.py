from manim import *
import numpy as np

class BackpropagationScene(Scene):
    def construct(self):
        # Define Network Structure
        input_layer = VGroup(*[Circle(radius=0.3, color=BLUE, fill_opacity=1) for _ in range(2)]).arrange(DOWN, buff=0.5)
        hidden_layer = VGroup(*[Circle(radius=0.3, color=GREEN, fill_opacity=1) for _ in range(3)]).arrange(DOWN, buff=0.5)
        output_layer = VGroup(*[Circle(radius=0.3, color=RED, fill_opacity=1) for _ in range(1)]).arrange(DOWN, buff=0.5)

        layers = VGroup(input_layer, hidden_layer, output_layer).arrange(RIGHT, buff=2)
        self.play(FadeIn(layers))

        # Add Layer Labels
        input_label = Text("Input").next_to(input_layer, UP)
        hidden_label = Text("Hidden").next_to(hidden_layer, UP)
        output_label = Text("Output").next_to(output_layer, UP)
        self.play(Write(input_label), Write(hidden_label), Write(output_label))

        # Draw Connections (Weights)
        connections_1 = VGroup()
        for i_node in input_layer:
            for h_node in hidden_layer:
                connections_1.add(Line(i_node.get_right(), h_node.get_left(), stroke_width=1, color=GRAY))

        connections_2 = VGroup()
        for h_node in hidden_layer:
            for o_node in output_layer:
                connections_2.add(Line(h_node.get_right(), o_node.get_left(), stroke_width=1, color=GRAY))

        self.play(Create(connections_1), Create(connections_2))
        self.wait(1)

        # --- Forward Pass ---
        self.play(Circumscribe(input_layer, color=YELLOW, time_width=2, fade_out=True))
        forward_arrows_1 = VGroup(*[Arrow(i_node.get_right(), h_node.get_left(), buff=0.1, max_tip_length_to_length_ratio=0.1, stroke_width=3, color=YELLOW) for i_node in input_layer for h_node in hidden_layer])
        self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in forward_arrows_1], lag_ratio=0.1))
        self.play(FadeOut(forward_arrows_1))
        self.play(Circumscribe(hidden_layer, color=YELLOW, time_width=2, fade_out=True))

        forward_arrows_2 = VGroup(*[Arrow(h_node.get_right(), o_node.get_left(), buff=0.1, max_tip_length_to_length_ratio=0.1, stroke_width=3, color=YELLOW) for h_node in hidden_layer for o_node in output_layer])
        self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in forward_arrows_2], lag_ratio=0.1))
        self.play(FadeOut(forward_arrows_2))
        self.play(Circumscribe(output_layer, color=YELLOW, time_width=2, fade_out=True))
        self.wait(1)

        # --- Error Calculation ---
        error_text = Text("Calculate Error", color=ORANGE).scale(0.7).next_to(output_layer, DOWN, buff=0.5)
        self.play(Write(error_text))
        self.play(Indicate(output_layer, color=ORANGE, scale_factor=1.5))
        self.wait(1)
        self.play(FadeOut(error_text))

        # --- Backward Pass (Backpropagation) ---
        backprop_title = Text("Backpropagation", color=PINK).to_edge(UP)
        self.play(Write(backprop_title))

        # Error signal from Output to Hidden
        backward_arrows_2 = VGroup()
        gradient_texts_2 = VGroup()
        for h_node in hidden_layer:
            for o_node in output_layer:
                arrow = Arrow(o_node.get_left(), h_node.get_right(), buff=0.1, max_tip_length_to_length_ratio=0.1, stroke_width=3, color=PINK)
                backward_arrows_2.add(arrow)
                gradient_text = MathTex(r"\nabla W_{ho}", color=PINK).scale(0.5).move_to(arrow.get_center() + DOWN * 0.3)
                gradient_texts_2.add(gradient_text)

        self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in backward_arrows_2], lag_ratio=0.1))
        self.play(AnimationGroup(*[Write(text) for text in gradient_texts_2], lag_ratio=0.1))
        self.play(Indicate(connections_2, color=PINK))
        self.play(FadeOut(backward_arrows_2), FadeOut(gradient_texts_2))

        # Error signal from Hidden to Input
        backward_arrows_1 = VGroup()
        gradient_texts_1 = VGroup()
        for i_node in input_layer:
            for h_node in hidden_layer:
                 arrow = Arrow(h_node.get_left(), i_node.get_right(), buff=0.1, max_tip_length_to_length_ratio=0.1, stroke_width=3, color=PINK)
                 backward_arrows_1.add(arrow)
                 gradient_text = MathTex(r"\nabla W_{ih}", color=PINK).scale(0.5).move_to(arrow.get_center() + DOWN * 0.3)
                 gradient_texts_1.add(gradient_text)

        self.play(AnimationGroup(*[GrowArrow(arrow) for arrow in backward_arrows_1], lag_ratio=0.1))
        self.play(AnimationGroup(*[Write(text) for text in gradient_texts_1], lag_ratio=0.1))
        self.play(Indicate(connections_1, color=PINK))
        self.play(FadeOut(backward_arrows_1), FadeOut(gradient_texts_1))
        self.wait(0.5)

        # --- Weight Update ---
        update_text = Text("Update Weights using Gradients", color=GREEN).scale(0.7).next_to(layers, DOWN, buff=1)
        self.play(Write(update_text))
        self.play(
            connections_1.animate.set_color(GREEN_E),
            connections_2.animate.set_color(GREEN_E),
            run_time=1.5
        )
        self.play(
            connections_1.animate.set_color(GRAY),
            connections_2.animate.set_color(GRAY),
            run_time=1.5
        )
        self.wait(2)
        self.play(FadeOut(update_text), FadeOut(backprop_title))
        self.play(FadeOut(layers), FadeOut(connections_1), FadeOut(connections_2), FadeOut(input_label), FadeOut(hidden_label), FadeOut(output_label))
        self.wait(1)
