import math
from manim import *

# Set the output directory
config.output_file = "./output/ball/RollingBallEnergyConservation"

class RollingBallEnergyConservation(Scene):
    def construct(self):
        # --- Configuration ---
        hill_color = BLUE
        ball_color = RED
        vector_color = YELLOW
        pe_color = GREEN
        ke_color = ORANGE
        total_e_color = PURPLE

        # --- Helper Functions ---
        def get_slope_point(x, slope_angle=PI / 6, hill_start_x=-5, hill_base_y=-2):
            """Calculates y coordinate on the slope for a given x."""
            return math.tan(slope_angle) * (x - hill_start_x) + hill_base_y

        def get_height(x, slope_angle=PI / 6, hill_start_x=-5, hill_base_y=-2):
            """Calculates height relative to the base."""
            return max(0, get_slope_point(x, slope_angle, hill_start_x, hill_base_y) - hill_base_y)

        # --- Scene Setup ---
        title = Text("Energy Conservation: Ball Rolling Down a Hill").to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # --- Create Hill and Ball ---
        slope_angle = PI / 8  # Angle of the slope
        hill_start_x = -5.5
        hill_end_x = 1.5
        hill_base_y = -2.5
        ball_radius = 0.3

        # Define the hill shape
        hill = Polygon(
            [hill_start_x, hill_base_y + get_height(hill_start_x, slope_angle, hill_start_x, hill_base_y), 0], # Top-left vertex adjusted for height
            [hill_end_x, hill_base_y, 0],  # Bottom-right vertex
            [hill_start_x, hill_base_y, 0],  # Bottom-left vertex
            color=hill_color,
            fill_opacity=0.7
        ).shift(LEFT * 1)

        # Create the path for the ball (the slope surface)
        slope_path = Line(
            hill.get_vertices()[0],
            hill.get_vertices()[1],
            stroke_width=0 # Make path invisible, ball will follow it
        )

        # Initial position of the ball at the top of the hill
        initial_ball_pos = slope_path.get_start() + UP * ball_radius / math.cos(slope_angle) + LEFT * ball_radius * math.sin(slope_angle)
        ball = Dot(point=initial_ball_pos, radius=ball_radius, color=ball_color)

        self.play(Create(hill))
        self.play(FadeIn(ball))
        self.wait(0.5)

        # --- Introduce Energy Concepts ---
        # Use ValueTrackers for dynamic values
        time = ValueTracker(0)
        # Simulate parameters (mass=1 for simplicity in visualization)
        m = 1
        g = 9.8
        # Corrected initial height calculation based on ball's actual starting y-position relative to the base
        initial_h = initial_ball_pos[1] - ball_radius - hill_base_y

        # Potential Energy (PE = mgh)
        pe_formula = MathTex("PE", "=", "m", "g", "h", color=pe_color).to_edge(RIGHT, buff=1).shift(UP*1.5)
        pe_value_text = VGroup(Text("PE = ", color=pe_color), DecimalNumber(m * g * initial_h, color=pe_color, num_decimal_places=1)).arrange(RIGHT).next_to(pe_formula, DOWN, buff=0.3)

        # Kinetic Energy (KE = 1/2 mv^2)
        # Use r-string or double backslash for LaTeX
        ke_formula = MathTex("KE", "=", r"{1\over 2}", "m", r"v^2", color=ke_color).next_to(pe_value_text, DOWN, buff=0.5)
        ke_value_text = VGroup(Text("KE = ", color=ke_color), DecimalNumber(0, color=ke_color, num_decimal_places=1)).arrange(RIGHT).next_to(ke_formula, DOWN, buff=0.3)

        # Total Energy (E = PE + KE)
        total_e_formula = MathTex("E", "=", "PE", "+", "KE", "=", "Constant", color=total_e_color).next_to(ke_value_text, DOWN, buff=0.5)
        total_e_value = m * g * initial_h # Initial total energy
        total_e_value_text = VGroup(Text("E = ", color=total_e_color), DecimalNumber(total_e_value, color=total_e_color, num_decimal_places=1)).arrange(RIGHT).next_to(total_e_formula, DOWN, buff=0.3)

        self.play(Write(pe_formula))
        self.play(Write(ke_formula))
        self.play(Write(total_e_formula))
        self.play(FadeIn(pe_value_text), FadeIn(ke_value_text), FadeIn(total_e_value_text))
        self.wait(2)

        # --- Initial State Analysis ---
        # Height indicator
        h_line = DashedLine(
            ball.get_center() + RIGHT * 0.1, # Start slightly right of ball center
            [ball.get_center()[0] + 0.1, hill_base_y, 0], # End at base level
            color=WHITE
        )
        h_label = MathTex("h", color=WHITE).next_to(h_line, RIGHT)
        # Velocity vector (initially zero)
        vel_vector = Vector([0,0,0], color=ke_color).move_to(ball.get_center()) # Zero length initially

        self.play(Create(h_line), Write(h_label))
        self.play(FadeIn(vel_vector))
        self.play(Indicate(pe_formula), Indicate(pe_value_text), Circumscribe(h_label))
        self.play(Indicate(ke_formula), Indicate(ke_value_text), Indicate(vel_vector))
        self.play(Indicate(total_e_formula), Indicate(total_e_value_text))
        self.wait(2)

        # --- Rolling Down Animation ---
        explanation_text = Text("As the ball rolls down:", t2c={"PE": pe_color, "KE": ke_color}).scale(0.7).to_edge(DOWN)
        explanation_pe = Text("Height (h) decreases -> PE decreases", t2c={"PE": pe_color}).scale(0.7).next_to(explanation_text, UP, aligned_edge=LEFT)
        explanation_ke = Text("Velocity (v) increases -> KE increases", t2c={"KE": ke_color}).scale(0.7).next_to(explanation_pe, UP, aligned_edge=LEFT)
        # Removed conflicting 'E' color mapping in t2c for the Text object below
        explanation_total = Text("Total Energy (E = PE + KE) remains constant", t2c={"PE": pe_color, "KE": ke_color}).scale(0.7).next_to(explanation_ke, UP, aligned_edge=LEFT)

        self.play(FadeIn(explanation_text), FadeIn(explanation_pe), FadeIn(explanation_ke), FadeIn(explanation_total))

        # Animation parameters
        run_time = 5 # Duration of the roll

        # Updaters for dynamic elements
        # Update height line and label
        h_line.add_updater(lambda mob: mob.become(DashedLine(
            ball.get_center() + RIGHT * 0.1,
            [ball.get_center()[0] + 0.1, hill_base_y, 0],
            color=WHITE
        )).set_opacity(1 if ball.get_center()[1] > hill_base_y + ball_radius + 0.01 else 0) ) # Hide when near base
        h_label.add_updater(lambda mob: mob.next_to(h_line, RIGHT).set_opacity(h_line.get_opacity()))

        # Update PE value display (calculate height from ball's y relative to base)
        pe_value_text[1].add_updater(lambda d: d.set_value(m * g * max(0, ball.get_center()[1] - ball_radius - hill_base_y)))

        # Update KE value display (derive velocity from energy conservation)
        # KE = Total E - PE
        ke_value_text[1].add_updater(lambda d: d.set_value(max(0, total_e_value - pe_value_text[1].get_value())))

        # Update Velocity Vector
        # v_mag = sqrt(2 * KE / m)
        # Direction is along the slope
        slope_direction = normalize(slope_path.get_end() - slope_path.get_start())
        vel_vector.add_updater(lambda mob: mob.become(
            Vector(slope_direction * np.sqrt(max(0, 2 * ke_value_text[1].get_value() / m)), color=ke_color)
            .move_to(ball.get_center()) # Use move_to for positioning based on center
        ))

        # Update Total Energy display (should remain constant)
        total_e_value_text[1].add_updater(lambda d: d.set_value(pe_value_text[1].get_value() + ke_value_text[1].get_value()))

        # Force vectors
        gravity_force_vec = Vector(DOWN * m * g * 0.3, color=WHITE).add_updater(lambda mob: mob.move_to(ball.get_center() + mob.get_vector()/2))
        gravity_label = MathTex(r"m\vec{g}", color=WHITE).scale(0.7).add_updater(lambda mob: mob.next_to(gravity_force_vec, DOWN))

        # Normal force
        normal_direction = rotate_vector(slope_direction, PI/2)
        normal_magnitude = m * g * math.cos(slope_angle) * 0.3
        normal_force_vec = Vector(normal_direction * normal_magnitude, color=PINK).add_updater(lambda mob: mob.move_to(ball.get_center() + mob.get_vector()/2))
        normal_label = MathTex(r"\vec{N}", color=PINK).scale(0.7).add_updater(lambda mob: mob.next_to(normal_force_vec, normal_direction))

        # Force parallel to slope
        parallel_magnitude = m * g * math.sin(slope_angle) * 0.3
        parallel_force_vec = Vector(slope_direction * parallel_magnitude, color=vector_color).add_updater(lambda mob: mob.move_to(ball.get_center() + mob.get_vector()/2))
        # Use r-string or double backslash
        parallel_label = MathTex(r"m g \sin \theta", color=vector_color).scale(0.7).add_updater(lambda mob: mob.next_to(parallel_force_vec, slope_direction * DOWN))

        self.play(FadeIn(gravity_force_vec, gravity_label, normal_force_vec, normal_label, parallel_force_vec, parallel_label))
        self.wait(1.5)


        # Animate the ball rolling
        self.play(
            MoveAlongPath(ball, slope_path, rate_func=rate_functions.ease_in_quad),
            run_time=run_time
        )

        # Clear updaters to freeze final state
        ball.clear_updaters()
        h_line.clear_updaters()
        h_label.clear_updaters()
        pe_value_text[1].clear_updaters()
        ke_value_text[1].clear_updaters()
        vel_vector.clear_updaters()
        total_e_value_text[1].clear_updaters()
        gravity_force_vec.clear_updaters()
        gravity_label.clear_updaters()
        normal_force_vec.clear_updaters()
        normal_label.clear_updaters()
        parallel_force_vec.clear_updaters()
        parallel_label.clear_updaters()

        # Set final values explicitly after clearing updaters to ensure accuracy
        final_h = max(0, ball.get_center()[1] - ball_radius - hill_base_y)
        final_pe = m * g * final_h
        final_ke = max(0, total_e_value - final_pe)
        pe_value_text[1].set_value(final_pe)
        ke_value_text[1].set_value(final_ke)
        total_e_value_text[1].set_value(final_pe + final_ke) # Should be close to initial total_e_value
        final_v_mag = np.sqrt(max(0, 2 * final_ke / m))
        vel_vector.become(Vector(slope_direction * final_v_mag, color=ke_color).move_to(ball.get_center()))
        h_line.become(DashedLine(ball.get_center() + RIGHT*0.1, [ball.get_center()[0]+0.1, hill_base_y, 0], color=WHITE)).set_opacity(1 if final_h > 0.01 else 0)
        h_label.next_to(h_line, RIGHT).set_opacity(h_line.get_opacity())
        gravity_force_vec.move_to(ball.get_center() + gravity_force_vec.get_vector()/2)
        gravity_label.next_to(gravity_force_vec, DOWN)
        normal_force_vec.move_to(ball.get_center() + normal_force_vec.get_vector()/2)
        normal_label.next_to(normal_force_vec, normal_direction)
        parallel_force_vec.move_to(ball.get_center() + parallel_force_vec.get_vector()/2)
        parallel_label.next_to(parallel_force_vec, slope_direction * DOWN)


        self.play(FadeOut(explanation_text, explanation_pe, explanation_ke, explanation_total))
        self.play(Indicate(total_e_value_text))
        self.wait(1)

        # --- Final State Analysis ---
        # Use a reference point for positioning that exists
        ref_point_final_text = total_e_value_text.get_corner(DL) + DOWN * 1.5
        final_pos_text = Text("Final State (Bottom):", color=WHITE).scale(0.7).move_to(ref_point_final_text, aligned_edge=UL)
        final_pe_text = Text("h ≈ 0 -> PE ≈ 0", t2c={"PE": pe_color}).scale(0.7).next_to(final_pos_text, DOWN, aligned_edge=LEFT)
        final_ke_text = Text("v is maximum -> KE is maximum", t2c={"KE": ke_color}).scale(0.7).next_to(final_pe_text, DOWN, aligned_edge=LEFT)
        final_total_text = Text("E = KE_max ≈ PE_initial", t2c={"E": total_e_color, "KE": ke_color, "PE": pe_color}).scale(0.7).next_to(final_ke_text, DOWN, aligned_edge=LEFT)

        self.play(Write(final_pos_text))
        self.play(Write(final_pe_text))
        self.play(Write(final_ke_text))
        self.play(Write(final_total_text))
        self.wait(3)

        # --- Derivation ---
        derivation_title = Text("Deriving Max Velocity:", color=YELLOW).scale(0.8).move_to(final_pos_text.get_center()).shift(UP*0.5)
        step1 = MathTex("E_{initial}", "=", "E_{final}", color=total_e_color).next_to(derivation_title, DOWN, buff=0.4)
        step2 = MathTex("PE_{initial}", "+", "KE_{initial}", "=", "PE_{final}", "+", "KE_{final}", color=WHITE).next_to(step1, DOWN, buff=0.4)
        # Use initial_h as calculated earlier
        step3 = MathTex(f"mgh", "+", "0", "=", "0", "+", r"{1 \over 2} m v_{max}^2", color=WHITE).next_to(step2, DOWN, buff=0.4)
        step4 = MathTex(f"mgh", "=", r"{1 \over 2} m v_{max}^2", color=WHITE).next_to(step3, DOWN, buff=0.4)
        step5 = MathTex(r"v_{max}^2", "=", f"2gh", color=WHITE).next_to(step4, DOWN, buff=0.4)
        step6 = MathTex(r"v_{max}", "=", r"\sqrt{2gh}", color=YELLOW).next_to(step5, DOWN, buff=0.4) # Use r-string

        # Replace existing final texts with derivation
        final_text_group = VGroup(final_pos_text, final_pe_text, final_ke_text, final_total_text)
        derivation_group = VGroup(derivation_title, step1, step2, step3, step4, step5, step6)

        self.play(FadeOut(final_text_group), FadeIn(derivation_title))
        self.play(Write(step1))
        self.wait(0.5)
        self.play(Write(step2))
        self.wait(1)
        self.play(TransformMatchingTex(step2.copy().move_to(step3), step3, path_arc=PI/2)) # Transform instead of Replace
        self.wait(1)
        self.play(TransformMatchingTex(step3.copy().move_to(step4), step4, path_arc=PI/2))
        self.wait(1)
        self.play(TransformMatchingTex(step4.copy().move_to(step5), step5, path_arc=PI/2))
        self.wait(1)
        self.play(TransformMatchingTex(step5.copy().move_to(step6), step6, path_arc=PI/2))
        self.play(Circumscribe(step6))
        self.wait(3)

        # --- Cleanup ---
        self.play(FadeOut(*self.mobjects)) # Fade out all mobjects currently on screen
        self.wait(1)
