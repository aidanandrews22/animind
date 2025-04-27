from manim import *
import numpy as np

class PointChargeInNonUniformBField(ThreeDScene):
    def construct(self):
        # Parameters
        q = 1.0  # Charge
        m = 1.0  # Mass
        v0 = 2.0  # Initial speed
        B0 = 1.0  # Base magnetic field strength
        alpha = 0.5 # Magnetic field gradient factor
        L = 5.0   # Height of the magnetic field region

        # Scene setup
        axes = ThreeDAxes(
            x_range=[-1, 6, 1],
            y_range=[-1, 6, 1],
            z_range=[-1, 1, 1],
            x_length=7,
            y_length=7,
            z_length=2,
            tips=False,
        )
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y").shift(UP*0.5) # Adjust label position slightly
        z_label = axes.get_z_axis_label("z").shift(OUT*0.5)
        labels = VGroup(x_label, y_label, z_label)
        self.set_camera_orientation(phi=75 * DEGREES, theta=-60 * DEGREES)
        self.add(axes, labels)

        # Magnetic Field Region Visualization
        field_region = Rectangle(
            width=axes.x_axis.number_to_point(6)[0] - axes.x_axis.number_to_point(0)[0], # Width from x=0 to x=6
            height=axes.y_axis.number_to_point(L)[1] - axes.y_axis.number_to_point(0)[1], # Height from y=0 to y=L
            stroke_width=1,
            stroke_color=BLUE,
            fill_opacity=0.3
        )
        # Align bottom-left corner with origin (0,0) in XY plane
        field_region.move_to(axes.c2p(3, L/2, 0), aligned_edge=ORIGIN)
        field_region.shift(axes.c2p(0, 0, 0) - field_region.get_corner(DL)) # Align DL corner to origin

        # Apply gradient - Stronger blue for larger x
        field_region.set_fill(BLUE, opacity=0.3)
        field_region.set_color_by_gradient(BLUE, DARK_BLUE) # Simple gradient

        self.add(field_region)
        field_label = Tex(r"$\mathbf{B}(x) = B_0(1+\\alpha x) \\hat{k}$", font_size=36).move_to(axes.c2p(4, L + 0.5, 0))
        self.add(field_label)

        # Particle setup
        particle = Dot3D(point=axes.c2p(0, -1, 0), radius=0.08, color=YELLOW)
        particle.velocity = v0 * UP # Initial velocity vector [0, v0, 0]
        particle.pos = particle.get_center() # Use numpy array for physics calculations
        particle.path = VMobject(color=YELLOW)
        particle.path.set_points_as_corners([particle.pos, particle.pos])

        lorentz_force_arrow = Arrow(start=particle.pos, end=particle.pos, color=RED, stroke_width=4, max_tip_length_to_length_ratio=0.15)

        def path_updater(mob, dt):
            # Store previous position for path drawing
            old_pos = mob.pos.copy()

            # Check if particle is inside the magnetic field region
            in_field = mob.pos[0] >= 0 and 0 <= mob.pos[1] <= L

            if in_field:
                # Calculate B field at current x position
                Bx = mob.pos[0]
                # Clamp Bx if needed, though it should stay positive
                current_B_mag = B0 * (1 + alpha * max(0, Bx))
                B_vector = current_B_mag * OUT # B is in +z direction (k_hat)

                # Calculate Lorentz force F = q(v x B)
                # Ensure velocity is a numpy array for cross product
                vel_vec = np.array(mob.velocity)
                F_lorentz = q * np.cross(vel_vec, B_vector)

                # Update acceleration, velocity, position (Euler integration)
                acc = F_lorentz / m
                mob.velocity = mob.velocity + acc * dt
                # Ensure speed remains constant (v = v0) - Project velocity onto sphere of radius v0
                mob.velocity = v0 * normalize(mob.velocity)
                mob.pos = mob.pos + mob.velocity * dt

                # Update Lorentz force arrow
                if np.linalg.norm(F_lorentz) > 1e-6: # Only show if force is significant
                    force_display_vec = normalize(F_lorentz) * 0.5 # Scaled for visibility
                    lorentz_force_arrow.put_start_and_end_on(mob.pos, mob.pos + force_display_vec)
                    lorentz_force_arrow.set_opacity(1)
                else:
                    lorentz_force_arrow.set_opacity(0)

            else: # Outside field (initial straight path or after exit)
                 mob.pos = mob.pos + mob.velocity * dt
                 lorentz_force_arrow.set_opacity(0)


            # Update particle Mobject position
            mob.move_to(mob.pos)
            # Update path
            mob.path.add_points_as_corners([mob.pos])


            # Stop condition: if particle exits the top boundary y=L
            if old_pos[1] < L and mob.pos[1] >= L:
                 # Calculate exact intersection point with y=L using linear interpolation
                 t_intersect = (L - old_pos[1]) / (mob.pos[1] - old_pos[1])
                 final_pos = old_pos + (mob.pos - old_pos) * t_intersect
                 mob.pos = final_pos # Snap to boundary
                 mob.move_to(mob.pos)
                 mob.path.add_points_as_corners([mob.pos]) # Add final point

                 # Remove updaters
                 particle.clear_updaters()
                 lorentz_force_arrow.clear_updaters()
                 lorentz_force_arrow.set_opacity(0) # Hide force after exit

                 # Add exit marker and final info
                 exit_dot = Dot3D(point=mob.pos, radius=0.1, color=RED)
                 final_velocity_vector = Arrow(start=mob.pos, end=mob.pos + normalize(mob.velocity)*1.0, color=GREEN, stroke_width=4, max_tip_length_to_length_ratio=0.15)
                 final_v_label = MathTex("v_f", font_size=30).next_to(final_velocity_vector.get_end(), normalize(mob.velocity))

                 x_exit = mob.pos[0]
                 final_angle = np.arctan2(mob.velocity[1], mob.velocity[0]) * 180/PI # Angle wrt +x
                 energy_text = MathTex(r"KE = \frac{1}{2} m v_0^2 \text{ (const)}", font_size=30)
                 exit_info_text = Tex(f"Exit at ({x_exit:.2f}, {L:.1f})", f"Angle = {final_angle:.1f} \\degree", font_size=30)
                 summary_text = VGroup(exit_info_text, energy_text).arrange(DOWN, aligned_edge=LEFT).next_to(field_region, DOWN, buff=0.5).shift(LEFT*2)


                 self.play(
                     Create(exit_dot),
                     GrowArrow(final_velocity_vector),
                     Write(final_v_label),
                     Write(summary_text),
                     run_time=1
                 )
                 self.wait(2) # Hold final frame


        # Animation Steps
        # 1. Particle enters from below y=0
        self.play(Create(particle))
        self.play(particle.animate.move_to(axes.c2p(0, 0, 0)), run_time=0.5 / v0) # Move to origin

        # 2. Particle moves through the field
        self.add(particle.path, lorentz_force_arrow)
        particle.add_updater(path_updater)
        # Add updater to force arrow AFTER path_updater ensures particle.pos is updated
        lorentz_force_arrow.add_updater(lambda m: m.move_to(particle.pos))

        # Let the simulation run until the stop condition in the updater is met
        self.wait(L / v0 * 3) # Estimate time; updater will handle the stop

        # Note: The wait time might need adjustment depending on parameters
        # The stop condition within the updater is the primary control

        # Ensure final state is held if updater didn't trigger final animations
        # (This is a fallback, the updater should handle it)
        if particle.has_updaters():
             particle.clear_updaters()
             lorentz_force_arrow.clear_updaters()
             lorentz_force_arrow.set_opacity(0)
             self.wait(2)


