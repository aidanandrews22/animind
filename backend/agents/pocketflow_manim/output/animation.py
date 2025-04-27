from manim import *
import numpy as np

class RollingBallOnHill(Scene):
    def construct(self):
        # Title
        title = Tex("Ball Rolling Down a Hill: Energy Conservation").to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Create the hill (a curved path)
        # Using a quadratic function for a simple hill shape
        hill = lambda x: -0.1 * (x + 5) * (x - 5) # Parabola opening downwards
        hill_path = ParametricFunction(lambda t: np.array([t, hill(t), 0]), t_range=[-6, 6], color=GREEN)
        hill_plot = FunctionGraph(hill, x_range=[-6, 6], color=GREEN)
        hill_group = VGroup(hill_plot).scale(0.8).shift(DOWN * 1.5)

        self.play(Create(hill_group))
        self.wait(0.5)

        # Create the ball
        ball_radius = 0.3
        ball_start_x = -4
        ball_start_pos = hill_group.get_point_from_function(ball_start_x)
        ball = Circle(radius=ball_radius, color=RED, fill_opacity=0.8)
        ball.move_to(ball_start_pos + UP * ball_radius) # Place ball tangent to the hill

        self.play(FadeIn(ball))
        self.wait(0.5)

        # --- Physics Explanation ---

        # 1. Initial State: Potential Energy
        initial_state_text = Tex("Initial State: Maximum Potential Energy").scale(0.7).next_to(title, DOWN, buff=0.5)
        self.play(Write(initial_state_text))

        # Show Potential Energy Formula
        pe_formula = MathTex(r"PE = mgh").scale(0.8).to_corner(UL).shift(DOWN*1)
        self.play(Write(pe_formula))

        # Visualize Initial Height
        h_line = DashedLine(ball.get_bottom(), np.array([ball.get_center()[0], hill_group.get_bottom()[1], 0]), color=YELLOW)
        h_label = MathTex(r"h").scale(0.7).next_to(h_line, RIGHT)
        self.play(Create(h_line), Write(h_label))
        self.wait(1)

        # Initial Vectors (Gravity)
        gravity_vec = Arrow(ball.get_center(), ball.get_center() + DOWN * 1.5, buff=0, color=WHITE)
        gravity_label = MathTex(r"\vec{F}_g = m\vec{g}").scale(0.7).next_to(gravity_vec, RIGHT)
        self.play(GrowArrow(gravity_vec), Write(gravity_label))
        self.wait(1)

        # Components of Gravity (Normal and Tangential)
        # Need to calculate the tangent and normal vectors at the starting point
        slope = hill_plot.get_derivative(ball_start_x)
        angle = np.arctan(slope)
        normal_vec_dir = np.array([-np.sin(angle), np.cos(angle), 0])
        tangent_vec_dir = np.array([np.cos(angle), np.sin(angle), 0])

        # Decompose gravity
        mg = 1.5 # Magnitude for visualization
        f_normal_mag = mg * np.cos(angle)
        f_tangent_mag = mg * np.sin(angle)

        f_normal = Arrow(ball.get_center(), ball.get_center() + normal_vec_dir * f_normal_mag, buff=0, color=BLUE)
        f_tangent = Arrow(ball.get_center(), ball.get_center() + tangent_vec_dir * f_tangent_mag, buff=0, color=ORANGE)
        f_normal_label = MathTex(r"\vec{F}_N").scale(0.6).next_to(f_normal.get_end(), normal_vec_dir * 0.5)
        f_tangent_label = MathTex(r"\vec{F}_{||}").scale(0.6).next_to(f_tangent.get_end(), tangent_vec_dir * 0.5)

        self.play(Transform(gravity_vec, VGroup(f_normal, f_tangent)), FadeOut(gravity_label),
                  Write(f_normal_label), Write(f_tangent_label))
        self.wait(1)
        self.play(FadeOut(f_normal, f_tangent, f_normal_label, f_tangent_label, gravity_vec))
        self.play(FadeOut(initial_state_text), FadeOut(h_line), FadeOut(h_label))

        # 2. Rolling Down: Energy Conversion
        rolling_text = Tex("Rolling: PE converts to KE (Translational + Rotational)").scale(0.7).next_to(title, DOWN, buff=0.5)
        self.play(Write(rolling_text))

        ke_formula = MathTex(r"KE = KE_{trans} + KE_{rot} = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2").scale(0.8).next_to(pe_formula, DOWN, align=LEFT)
        self.play(Write(ke_formula))
        self.wait(1)

        # Total Energy Conservation
        conservation_formula = MathTex(r"E_{total} = PE_i + KE_i = PE_f + KE_f").scale(0.8).next_to(ke_formula, DOWN, align=LEFT)
        initial_cond = MathTex(r"KE_i = 0 	ext{ (starts from rest)}").scale(0.7).next_to(conservation_formula, DOWN, align=LEFT)
        self.play(Write(conservation_formula), Write(initial_cond))
        self.wait(1)

        # Animate the ball rolling down
        # We'll use an updater to handle physics approximately
        # Define parameters (mass, radius, gravity, moment of inertia for solid sphere)
        m = 1.0
        r = ball_radius
        g = 9.8
        I = 0.4 * m * r**2 # Moment of inertia for a solid sphere: (2/5)mr^2

        # Variable tracker for position along the path (parameter t)
        t_tracker = ValueTracker(ball_start_x)

        # Function to update ball position and rotation
        def update_ball(mob, dt):
            t = t_tracker.get_value()
            current_pos = hill_group.get_point_from_function(t)
            mob.move_to(current_pos + UP * r)

            # Approximate angular velocity based on linear velocity
            # This is complex on a curve; we'll simplify
            # v = sqrt(2gh / (1 + I/(mr^2))) -> calculate v based on height drop
            initial_h = hill(ball_start_x)
            current_h = hill(t)
            delta_h = initial_h - current_h
            if delta_h > 0:
                v_squared = (2 * m * g * delta_h) / (m + I / r**2)
                v = np.sqrt(v_squared)
                omega = v / r # Angular velocity
                # Calculate distance traveled along the curve (approximation)
                arc_length = np.abs(t - ball_start_x) # Simplified, needs better arc length calculation
                angle_rotated = -arc_length / r # Rotation angle
                mob.rotate(angle_rotated, about_point=mob.get_center())
            else:
                v = 0
                omega = 0

        # Updater for ball position and rotation (simplified)
        # A proper physics simulation is more involved
        ball.add_updater(update_ball)

        # Vectors during motion (Velocity and Acceleration components)
        velocity_vec = Arrow(color=CYAN)
        accel_vec = Arrow(color=YELLOW)
        vel_label = MathTex(r"\vec{v}").scale(0.6).set_color(CYAN)
        accel_label = MathTex(r"\vec{a}").scale(0.6).set_color(YELLOW)

        def update_vectors(mob):
            t = t_tracker.get_value()
            if t < 5.9: # Avoid end of range issues
                # Calculate velocity (tangent to the path)
                deriv = hill_plot.get_derivative(t)
                tangent_vector = np.array([1, deriv, 0])
                tangent_unit_vec = tangent_vector / np.linalg.norm(tangent_vector)

                # Calculate speed (simplified from energy)
                initial_h = hill(ball_start_x)
                current_h = hill(t)
                delta_h = initial_h - current_h
                if delta_h > 0:
                     v_squared = (2 * m * g * delta_h) / (m + I / r**2)
                     v_mag = np.sqrt(v_squared)
                else:
                    v_mag = 0

                # Update velocity vector
                velocity_vec.put_start_and_end_on(ball.get_center(), ball.get_center() + tangent_unit_vec * v_mag * 0.5) # Scale for visualization
                vel_label.next_to(velocity_vec.get_end(), tangent_unit_vec * 0.1)

                # Acceleration (tangential component drives speed change)
                # a_tangent = (m*g*sin(theta)) / (m + I/r^2)
                slope = deriv
                angle = np.arctan(slope)
                a_tangent_mag = (m * g * np.sin(angle)) / (m + I / r**2)

                # Update acceleration vector (showing tangential component for simplicity)
                accel_vec.put_start_and_end_on(ball.get_center(), ball.get_center() + tangent_unit_vec * a_tangent_mag * 0.2) # Scale for viz
                accel_label.next_to(accel_vec.get_end(), tangent_unit_vec * 0.1)
            else:
                velocity_vec.put_start_and_end_on(ball.get_center(), ball.get_center())
                accel_vec.put_start_and_end_on(ball.get_center(), ball.get_center())

        vectors_group = VGroup(velocity_vec, accel_vec, vel_label, accel_label)
        vectors_group.add_updater(update_vectors)

        self.play(FadeIn(vectors_group))

        # Animate the ball rolling to the bottom
        self.play(t_tracker.animate.set_value(4), run_time=5, rate_func=linear) # Adjust end value and runtime
        self.wait(0.5)

        ball.remove_updater(update_ball)
        vectors_group.remove_updater(update_vectors)
        self.play(FadeOut(vectors_group))

        # 3. Final State: Maximum Kinetic Energy (at lowest point)
        self.play(FadeOut(rolling_text, initial_cond))
        final_state_text = Tex("Final State (Lowest Point): Maximum Kinetic Energy").scale(0.7).next_to(title, DOWN, buff=0.5)
        self.play(Write(final_state_text))

        # Show final energy equation state
        final_energy = MathTex(r"E_{total} = PE_{min} + KE_{max}").scale(0.8).next_to(conservation_formula, DOWN, align=LEFT)
        self.play(Write(final_energy))
        self.wait(2)

        # Clear formulas
        self.play(FadeOut(pe_formula, ke_formula, conservation_formula, final_energy))

        # Derivations (Example: Speed at the bottom)
        deriv_title = Tex("Derivation: Speed at the Bottom").scale(0.8).to_corner(UL)
        self.play(FadeOut(title), Write(deriv_title))

        steps = VGroup(
            MathTex(r"E_{initial} = E_{final}"),
            MathTex(r"PE_i + KE_i = PE_f + KE_f"),
            MathTex(r"mgh + 0 = 0 + (KE_{trans} + KE_{rot})"),
            MathTex(r"mgh = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2"),
            MathTex(r"I = \frac{2}{5}mr^2 	ext{ (solid sphere), } \omega = v/r"),
            MathTex(r"mgh = \frac{1}{2}mv^2 + \frac{1}{2}(\frac{2}{5}mr^2)(\frac{v}{r})^2"),
            MathTex(r"mgh = \frac{1}{2}mv^2 + \frac{1}{5}mv^2"),
            MathTex(r"mgh = \frac{7}{10}mv^2"),
            MathTex(r"v = \sqrt{\frac{10}{7}gh}")
        ).scale(0.7).arrange(DOWN, aligned_edge=LEFT).next_to(deriv_title, DOWN, buff=0.3)

        for i, step in enumerate(steps):
            self.play(Write(step))
            if i < len(steps) - 1:
                 self.play(steps[i+1].animate.next_to(steps[i], DOWN, aligned_edge=LEFT, buff=0.2))
            self.wait(1.5)

        self.wait(3)

        # Final Fade Out
        self.play(FadeOut(ball), FadeOut(hill_group), FadeOut(steps), FadeOut(deriv_title), FadeOut(final_state_text))
        self.wait(1)
