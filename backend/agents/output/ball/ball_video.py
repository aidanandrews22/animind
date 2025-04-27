from manim import *
import numpy as np

class BallRollingDownHill(Scene):
    def construct(self):
        # --- Configuration ---
        incline_angle = PI / 6  # 30 degrees incline
        gravity_acc = 9.8
        ball_radius = 0.3
        ball_mass = 1.0  # Assume mass = 1 for simplicity in energy calcs
        incline_length = 8
        friction_coeff = 0.1 # Coefficient of rolling friction (optional, can be zero)

        # --- Scene Setup ---
        # Create the inclined plane (hill)
        # Positioned slightly left and down to center the animation
        incline_start = LEFT * 4 + UP * 1
        incline_end = incline_start + incline_length * np.array([np.cos(incline_angle), -np.sin(incline_angle), 0])
        incline = Line(incline_start, incline_end, stroke_width=6, color=BLUE)
        # Justification: Blue color for the static environment (hill). Stroke width for visibility.

        # Create the ground line
        ground = Line(incline_start + LEFT*2 - np.array([0, ball_radius, 0]), incline_end + RIGHT*2 - np.array([0, ball_radius, 0]), color=GREEN)
        # Justification: Green for the ground. Positioned below the incline.

        self.play(Create(incline), Create(ground))
        self.wait(0.5)

        # --- Ball Setup ---
        # Initial position of the ball at the top of the incline
        ball_initial_center = incline_start + np.array([0, ball_radius, 0]) / np.cos(incline_angle) # Adjust for radius contact
        ball = Circle(radius=ball_radius, color=RED, fill_opacity=0.8)
        ball.move_to(ball_initial_center)
        # Justification: Red color for the main dynamic object (ball). Fill opacity for better visibility.

        # Add a line inside the ball to show rotation
        ball_rotation_marker = Line(ball.get_center(), ball.get_center() + ball_radius * UP, color=WHITE, stroke_width=2)
        # Justification: White marker contrasts with red ball, thin stroke.

        self.play(FadeIn(ball), FadeIn(ball_rotation_marker))
        self.wait(0.5)

        # --- Physics Calculations ---
        g_parallel = gravity_acc * np.sin(incline_angle)
        g_perpendicular = gravity_acc * np.cos(incline_angle)
        # Acceleration down the slope (simplified, ignoring rotational inertia for now)
        # For a solid sphere, I = 2/5 * m * r^2. a = (m*g*sin(theta)) / (m + I/r^2) = (m*g*sin(theta)) / (m + 2/5*m) = (g*sin(theta)) / (1 + 2/5) = 5/7 * g * sin(theta)
        acceleration = (5/7) * g_parallel

        # Time to reach the bottom
        # d = 1/2 * a * t^2 => t = sqrt(2 * d / a)
        time_to_bottom = np.sqrt(2 * incline_length / acceleration)

        # --- Vectors ---
        # Gravity vector (constant)
        gravity_vector = Arrow(ball.get_center(), ball.get_center() + DOWN * ball_mass * gravity_acc * 0.3, buff=0, color=YELLOW)
        # Justification: Yellow for gravity, scaled for visual balance (0.3 factor).

        # Normal force vector (updates position)
        normal_force_vec_dir = np.array([-np.sin(incline_angle), np.cos(incline_angle), 0])
        normal_force_mag = ball_mass * g_perpendicular * 0.3 # Scaled
        normal_force_vector = Arrow(ball.get_center(), ball.get_center() + normal_force_vec_dir * normal_force_mag, buff=0, color=GREEN_B)
        # Justification: Green_B for normal force, perpendicular to incline.

        # Component vectors (updates position)
        g_parallel_vec_dir = np.array([np.cos(incline_angle), -np.sin(incline_angle), 0])
        g_perp_vec_dir = np.array([-np.sin(incline_angle), -np.cos(incline_angle), 0]) # Note: direction adjusted for visualization origin
        g_parallel_vector = Arrow(ball.get_center(), ball.get_center() + g_parallel_vec_dir * ball_mass * g_parallel * 0.3, buff=0, color=ORANGE)
        g_perp_vector = Arrow(ball.get_center(), ball.get_center() + g_perp_vec_dir * ball_mass * g_perpendicular * 0.3, buff=0, color=PURPLE)
        # Justification: Orange and Purple to distinguish components from main gravity vector.

        # Velocity vector (updates position and magnitude)
        velocity_vector = Arrow(ball.get_center(), ball.get_center(), buff=0, color=CYAN)
        # Justification: Cyan for velocity, starts at zero length.

        # Add updaters to keep vectors attached to the ball
        gravity_vector.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + DOWN * ball_mass * gravity_acc * 0.3))
        normal_force_vector.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + normal_force_vec_dir * normal_force_mag))
        g_parallel_vector.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + g_parallel_vec_dir * ball_mass * g_parallel * 0.3))
        g_perp_vector.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + g_perp_vec_dir * ball_mass * g_perpendicular * 0.3))
        velocity_vector.add_updater(lambda m: m.put_start_and_end_on(ball.get_center(), ball.get_center() + g_parallel_vec_dir * ball.velocity_val * 0.5)) # Scale velocity vector for visibility

        # Add labels for vectors
        g_label = MathTex("m\\vec{g}", color=YELLOW).next_to(gravity_vector.get_end(), DOWN*0.5)
        n_label = MathTex("\\vec{N}", color=GREEN_B).next_to(normal_force_vector.get_end(), normal_force_vec_dir*0.5)
        gp_label = MathTex("m\\vec{g}_{\\parallel}", color=ORANGE).next_to(g_parallel_vector.get_end(), g_parallel_vec_dir*0.5 + DOWN*0.2)
        gperp_label = MathTex("m\\vec{g}_{\perp}", color=PURPLE).next_to(g_perp_vector.get_end(), g_perp_vec_dir*0.5)
        v_label = MathTex("\\vec{v}", color=CYAN).next_to(velocity_vector, UP, buff=0.1)

        g_label.add_updater(lambda m: m.next_to(gravity_vector.get_end(), DOWN*0.5))
        n_label.add_updater(lambda m: m.next_to(normal_force_vector.get_end(), normal_force_vec_dir*0.5))
        gp_label.add_updater(lambda m: m.next_to(g_parallel_vector.get_end(), g_parallel_vec_dir*0.5 + DOWN*0.2))
        gperp_label.add_updater(lambda m: m.next_to(g_perp_vector.get_end(), g_perp_vec_dir*0.5))
        v_label.add_updater(lambda m: m.next_to(velocity_vector.get_end() + g_parallel_vec_dir*0.1, UP, buff=0.1).set_opacity(1 if ball.velocity_val > 0.1 else 0)) # Hide label if velocity is near zero

        self.play(
            Create(gravity_vector), Create(normal_force_vector),
            Create(g_parallel_vector), Create(g_perp_vector),
            Create(velocity_vector),
            Write(g_label), Write(n_label), Write(gp_label), Write(gperp_label), Write(v_label)
        )
        self.wait(1)

        # --- Energy Visualization ---
        # Use ValueTrackers to store energy values
        pe_tracker = ValueTracker(ball_mass * gravity_acc * (ball.get_center()[1] - ground.get_center()[1])) # Initial PE relative to ground
        ke_tracker = ValueTracker(0) # Initial KE
        total_e_tracker = ValueTracker(pe_tracker.get_value()) # Initial Total Energy

        # Create energy bars
        pe_bar = Rectangle(height=2, width=0.5, fill_color=BLUE, fill_opacity=0.7).to_corner(UR).shift(LEFT*1.5)
        ke_bar = Rectangle(height=0, width=0.5, fill_color=ORANGE, fill_opacity=0.7).next_to(pe_bar, RIGHT, buff=0.2)
        pe_label = MathTex("PE", color=BLUE).next_to(pe_bar, UP)
        ke_label = MathTex("KE", color=ORANGE).next_to(ke_bar, UP)
        # Justification: Blue for Potential, Orange for Kinetic, standard contrasting colors. Bars provide clear visual magnitude. Positioned top-right corner.

        # Add updaters for energy bars
        pe_bar.add_updater(lambda m: m.set_height(pe_tracker.get_value() * 0.1, stretch=True).align_to(pe_bar, DOWN)) # Scale height for visibility
        ke_bar.add_updater(lambda m: m.set_height(ke_tracker.get_value() * 0.1, stretch=True).align_to(ke_bar, DOWN)) # Scale height for visibility

        # Energy text labels (numerical values)
        pe_text = MathTex("PE = ", color=BLUE).to_corner(UR).shift(LEFT*3.5 + DOWN*0.5)
        ke_text = MathTex("KE = ", color=ORANGE).next_to(pe_text, DOWN, aligned_edge=LEFT)
        total_e_text = MathTex("E_{total} = ", color=WHITE).next_to(ke_text, DOWN, aligned_edge=LEFT)

        pe_value_text = DecimalNumber(pe_tracker.get_value(), num_decimal_places=1, color=BLUE).next_to(pe_text, RIGHT)
        ke_value_text = DecimalNumber(ke_tracker.get_value(), num_decimal_places=1, color=ORANGE).next_to(ke_text, RIGHT)
        total_e_value_text = DecimalNumber(total_e_tracker.get_value(), num_decimal_places=1, color=WHITE).next_to(total_e_text, RIGHT)

        pe_value_text.add_updater(lambda d: d.set_value(pe_tracker.get_value()).next_to(pe_text, RIGHT))
        ke_value_text.add_updater(lambda d: d.set_value(ke_tracker.get_value()).next_to(ke_text, RIGHT))
        # Total energy should remain constant (ideally)
        # total_e_value_text.add_updater(lambda d: d.set_value(pe_tracker.get_value() + ke_tracker.get_value()).next_to(total_e_text, RIGHT))

        energy_group = VGroup(pe_bar, ke_bar, pe_label, ke_label, pe_text, ke_text, total_e_text, pe_value_text, ke_value_text, total_e_value_text)
        self.play(FadeIn(energy_group))
        self.wait(1)

        # --- Equations ---
        # Energy conservation equation
        energy_eq = MathTex("PE_i + KE_i", "=", "PE_f + KE_f", color=WHITE).to_corner(UL).scale(0.8)
        energy_eq_detail = MathTex("mgh_i + \\frac{1}{2}mv_i^2", "=", "mgh_f + \\frac{1}{2}mv_f^2 + \\frac{1}{2}I\\omega_f^2", color=WHITE).next_to(energy_eq, DOWN, aligned_edge=LEFT).scale(0.7)
        # Justification: White color for general equations. Positioned top-left corner. Includes rotational KE.

        # Derivation of acceleration (simplified)
        accel_eq = MathTex("a = \\frac{g \\sin(\\theta)}{1 + I/(mr^2)}", "=", "\\frac{5}{7} g \\sin(\\theta)", color=WHITE).next_to(energy_eq_detail, DOWN, aligned_edge=LEFT).scale(0.7)
        # Justification: Shows the formula for acceleration including rotational inertia for a sphere.

        self.play(Write(energy_eq))
        self.wait(0.5)
        self.play(Write(energy_eq_detail))
        self.wait(0.5)
        self.play(Write(accel_eq))
        self.wait(2)

        # --- Animation ---
        # Custom updater function for the ball's motion and energy calculation
        ball.time_elapsed = 0
        ball.velocity_val = 0
        ball.dist_rolled = 0
        ball.angle_rotated = 0

        def update_ball(mob, dt):
            # Update time and distance
            mob.time_elapsed += dt
            # Calculate new velocity: v = a * t
            mob.velocity_val = acceleration * mob.time_elapsed
            # Calculate distance moved this frame: delta_d = v_avg * dt (more accurate: d = v_initial*dt + 0.5*a*dt^2)
            delta_d = mob.velocity_val * dt - 0.5 * acceleration * dt**2 # Distance covered in this dt
            mob.dist_rolled += delta_d

            # Calculate new position along the incline
            new_pos = ball_initial_center + mob.dist_rolled * g_parallel_vec_dir
            mob.move_to(new_pos)

            # Calculate rotation angle: angle = distance / radius
            mob.angle_rotated -= delta_d / ball_radius # Negative for clockwise rotation when moving down-right
            ball_rotation_marker.rotate(-delta_d / ball_radius, about_point=mob.get_center())
            ball_rotation_marker.move_to(mob.get_center()) # Ensure marker stays centered

            # Update energy values
            current_height = mob.get_center()[1] - ground.get_center()[1]
            current_pe = ball_mass * gravity_acc * current_height
            # KE = Translational KE + Rotational KE = 1/2*m*v^2 + 1/2*I*omega^2
            # For solid sphere I = 2/5*m*r^2, omega = v/r
            # KE = 1/2*m*v^2 + 1/2*(2/5*m*r^2)*(v/r)^2 = 1/2*m*v^2 + 1/5*m*v^2 = 7/10*m*v^2
            current_ke = (7/10) * ball_mass * mob.velocity_val**2

            pe_tracker.set_value(max(current_pe, 0)) # Ensure PE doesn't go negative
            ke_tracker.set_value(current_ke)
            # total_e_tracker.set_value(current_pe + current_ke) # Update total energy (should be constant)

        # Add the updater to the ball
        ball.add_updater(update_ball)

        # Animate the ball rolling down
        self.play(
            # We don't use a direct animation like MoveAlongPath,
            # instead, we let the updater handle the motion over time.
            # We just need Manim to progress time.
            Wait(time_to_bottom),
            run_time=time_to_bottom,
            rate_func=linear # Motion is governed by physics updater, not rate_func here
        )

        # Remove updater once animation is done to prevent issues
        ball.remove_updater(update_ball)
        # Ensure final values are set correctly
        final_v = acceleration * time_to_bottom
        final_ke = (7/10) * ball_mass * final_v**2
        pe_tracker.set_value(0)
        ke_tracker.set_value(final_ke)
        # total_e_value_text.set_value(pe_tracker.get_value() + ke_tracker.get_value()) # Set final total E display

        self.wait(2) # Hold the final state

        # --- Optional: Show Rate of Change (Derivative) ---
        deriv_text = MathTex(
            "\\frac{dE_{total}}{dt} = \\frac{d}{dt}(PE + KE) = 0",
            "\\implies \\frac{d(PE)}{dt} = -\\frac{d(KE)}{dt}"
        ).scale(0.7).to_corner(DL).set_color(YELLOW)
        # Justification: Yellow to highlight this concept. Positioned bottom-left. Shows energy conservation differential form.

        self.play(Write(deriv_text))
        self.wait(2)

        # Fade out everything
        self.play(FadeOut(VGroup(*self.mobjects))) # Fade out all mobjects
