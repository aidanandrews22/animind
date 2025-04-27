from manim import *
import numpy as np

class PointChargeInMagneticField(Scene):
    def construct(self):
        # --- Constants ---
        q = 1.0
        m = 1.0
        v0 = 2.0 # Initial speed
        B0 = 0.8 # Base magnetic field strength
        alpha = 0.4 # Field gradient factor
        L = 6.0 # Height of the field region
        x_max = 5.0 # Max x for axes/region visualization

        # --- Setup Scene ---
        axes = ThreeDAxes(
            x_range=[-1, x_max + 1, 1],
            y_range=[-1, L + 1, 1],
            z_range=[-1, 1, 1],
            x_length=7, # Adjusted length
            y_length=7,
            z_length=2,
            tips=False, # Hide arrow tips on axes
        )
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y", edge=UP)

        self.play(Write(axes), Write(x_label), Write(y_label))

        # --- Magnetic Field Region ---
        field_rect_bottom_left = axes.c2p(0, 0, 0)
        field_rect_top_right = axes.c2p(x_max, L, 0)
        field_region = Rectangle(
            width=field_rect_top_right[0] - field_rect_bottom_left[0],
            height=field_rect_top_right[1] - field_rect_bottom_left[1],
            stroke_width=1,
            fill_opacity=0.3,
        )
        # Apply gradient - Blue E (weak) to Blue A (strong)
        field_region.set_color(color=[BLUE_E, BLUE_A], gradient_direction=RIGHT)
        field_region.move_to(field_rect_bottom_left, aligned_edge=DL) # Align bottom-left corner to origin

        b_field_label = MathTex("B(x) = B_0(1+\alpha x) \hat{k}", font_size=24)
        # Position label near the top right of the field region
        label_pos = axes.c2p(x_max, L, 0)
        b_field_label.next_to(label_pos, UR, buff=0.2)

        self.play(FadeIn(field_region), Write(b_field_label))

        # --- Particle ---
        initial_y = -0.5
        particle = Dot(point=axes.c2p(0, initial_y, 0), color=RED, radius=0.08)
        particle.velocity = np.array([0.0, v0, 0.0]) # Store initial velocity (physical units)

        # --- Path Trace ---
        path = VMobject(color=YELLOW)
        path.set_points_as_corners([particle.get_center(), particle.get_center()]) # Start path at initial pos

        # --- Lorentz Force Arrow ---
        lorentz_force_arrow = Arrow(
            start=particle.get_center(),
            end=particle.get_center(), # Initially zero length
            color=RED,
            buff=0,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2,
        )
        lorentz_force_arrow.force_vector = np.array([0.0, 0.0, 0.0]) # Store physical force vector

        # --- Simulation Variables ---
        # Using a ValueTracker allows using Manim's animation system for smooth simulation
        time = ValueTracker(0)
        dt = 0.01 # Simulation time step, used in updater logic

        particle_state = {
            'exit_pos_manim': None, # Position in Manim coordinates where particle exits
            'exit_vel_phys': None, # Velocity in physical units when particle exits
            'exited': False
        }

        # --- Animation ---
        self.play(Create(particle))

        # Initial movement to the field boundary (y=0)
        entry_time = abs(initial_y / v0)
        self.play(
            particle.animate.move_to(axes.c2p(0, 0, 0)),
            run_time=entry_time
        )
        # Ensure particle velocity is stored correctly after initial move
        particle.velocity = np.array([0.0, v0, 0.0])
        path.start_new_path(axes.c2p(0,0,0)) # Start tracing path from origin

        # Function to update particle state based on physics
        def update_particle_physics(mob, dt):
            if particle_state['exited']:
                return # Stop updating after exit

            # Get current position (Manim coords) and velocity (physical units)
            current_pos_manim = mob.get_center()
            current_vel_phys = mob.velocity

            # Convert Manim position to physical coordinates
            current_pos_phys = axes.p2c(current_pos_manim)

            # Check if inside the magnetic field (x >= 0 and y < L)
            if current_pos_phys[0] >= 0 and current_pos_phys[1] < L:
                # Calculate B field at current x (physical units)
                Bx = B0 * (1 + alpha * current_pos_phys[0])
                B_vec = np.array([0, 0, Bx])

                # Calculate Lorentz force (physical units)
                force_phys = q * np.cross(current_vel_phys, B_vec)
                lorentz_force_arrow.force_vector = force_phys # Store for arrow updater

                # Update velocity using Euler method (physical units)
                new_vel_phys = current_vel_phys + (force_phys / m) * dt

                # --- CRITICAL: Ensure speed remains constant ---
                speed = np.linalg.norm(new_vel_phys)
                if speed > 1e-8: # Avoid division by zero or normalizing zero vector
                   new_vel_phys = (new_vel_phys / speed) * v0
                mob.velocity = new_vel_phys # Store updated physical velocity

                # Update position using Euler method (physical units)
                # Use the *average* velocity over the timestep for better accuracy (RK2 midpoint approx)
                # avg_vel_phys = (current_vel_phys + new_vel_phys) / 2.0
                # new_pos_phys = current_pos_phys + avg_vel_phys * dt
                # Sticking to simple Euler for now:
                new_pos_phys = current_pos_phys + new_vel_phys * dt

                # Convert new physical position back to Manim coordinates
                new_pos_manim = axes.c2p(*new_pos_phys)
                mob.move_to(new_pos_manim)

                # Check for exit condition (y >= L)
                if new_pos_phys[1] >= L:
                    # Linearly interpolate to find exact exit point at y=L
                    # Proportion of overshoot = (new_y - L) / (new_y - old_y) = (new_y - L) / (vel_y * dt)
                    overshoot_y = new_pos_phys[1] - L
                    last_vel_y = new_vel_phys[1]
                    if abs(last_vel_y) > 1e-6:
                       dt_correction = overshoot_y / last_vel_y
                       exit_pos_phys = new_pos_phys - new_vel_phys * dt_correction
                    else: # Vertical velocity is tiny, approx exit as current pos corrected to L
                       exit_pos_phys = np.array([new_pos_phys[0], L, new_pos_phys[2]])

                    particle_state['exit_pos_manim'] = axes.c2p(*exit_pos_phys)
                    particle_state['exit_vel_phys'] = new_vel_phys
                    particle_state['exited'] = True
                    mob.move_to(particle_state['exit_pos_manim']) # Move particle exactly to exit point

            else: # Outside field (x < 0 or y >= L)
                # If y >= L, particle has exited or was already above
                if current_pos_phys[1] >= L and not particle_state['exited']:
                    particle_state['exit_pos_manim'] = current_pos_manim
                    particle_state['exit_vel_phys'] = current_vel_phys
                    particle_state['exited'] = True
                    # No force applied if exited straight up before entering field region
                    lorentz_force_arrow.force_vector = np.array([0.0, 0.0, 0.0])

                # If x < 0 (shouldn't happen based on entry), just continue straight
                elif not particle_state['exited']:
                    new_pos_phys = current_pos_phys + current_vel_phys * dt
                    new_pos_manim = axes.c2p(*new_pos_phys)
                    mob.move_to(new_pos_manim)
                    lorentz_force_arrow.force_vector = np.array([0.0, 0.0, 0.0])


        # Function to update the path trace
        def update_path_trace(path_mob):
            if not particle_state['exited']:
                path_mob.add_points_as_corners([particle.get_center()])

        # Function to update the Lorentz force arrow visualization
        def update_force_arrow_vis(arrow_mob):
            if not particle_state['exited']:
                force_magnitude = np.linalg.norm(lorentz_force_arrow.force_vector)
                if force_magnitude > 1e-6: # Only show if force is significant
                    force_direction = lorentz_force_arrow.force_vector / force_magnitude
                    # Scale arrow length based on force magnitude relative to initial force
                    initial_force_mag = abs(q * v0 * B0)
                    target_length = 0.6 * (force_magnitude / initial_force_mag) if initial_force_mag > 1e-6 else 0.5
                    target_length = np.clip(target_length, 0.1, 0.8) # Clamp length

                    arrow_mob.put_start_and_end_on(
                        particle.get_center(),
                        particle.get_center() + force_direction * target_length
                    )
                    arrow_mob.set_opacity(1)
                else:
                    arrow_mob.set_opacity(0) # Hide if force is zero
            else:
                 arrow_mob.set_opacity(0) # Hide after exit

        # Add updaters to objects
        particle.add_updater(update_particle_physics)
        path.add_updater(update_path_trace)
        lorentz_force_arrow.add_updater(update_force_arrow_vis)

        # Add objects with updaters to the scene
        self.add(path, particle, lorentz_force_arrow)

        # Run the simulation by animating the time variable
        # Estimate simulation time: roughly L/v0 for vertical travel, but path is longer. Add buffer.
        estimated_time = (L / v0) * 2.5
        self.play(time.animate.set_value(estimated_time), rate_func=linear, run_time=estimated_time)

        # --- Post-Simulation ---
        # Ensure updaters are removed
        particle.clear_updaters()
        lorentz_force_arrow.clear_updaters()
        path.clear_updaters()

        # Check if particle exited and display final info
        if particle_state['exited'] and particle_state['exit_pos_manim'] is not None:
            exit_dot = Dot(particle_state['exit_pos_manim'], color=YELLOW, radius=0.1)
            self.play(FadeIn(exit_dot, scale=1.5))

            # Final velocity vector
            final_vel_phys = particle_state['exit_vel_phys']
            # Project velocity onto XY plane for Manim arrow direction
            final_vel_dir_manim = normalize(np.array([final_vel_phys[0], final_vel_phys[1], 0.0]))

            final_vel_arrow = Arrow(
                start=exit_dot.get_center(),
                end=exit_dot.get_center() + final_vel_dir_manim * 0.8, # Length 0.8
                color=GREEN,
                buff=0,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.2
            )
            final_vel_label = MathTex("v_f", font_size=24).next_to(final_vel_arrow.get_end(), UR, buff=0.1)
            self.play(GrowArrow(final_vel_arrow), Write(final_vel_label))

            # Final Text
            exit_pos_phys = axes.p2c(particle_state['exit_pos_manim'])
            exit_x_str = f"{exit_pos_phys[0]:.2f}"
            # Exit y should be exactly L due to interpolation
            exit_y_str = f"{L:.2f}"

            # Calculate final angle theta relative to +x axis
            angle_rad = np.arctan2(final_vel_phys[1], final_vel_phys[0])
            angle_deg = np.degrees(angle_rad)
            angle_str = f"{angle_deg:.1f}^\circ"

            # Verify final speed
            final_speed = np.linalg.norm(final_vel_phys)
            speed_text = f"|v_f| = {final_speed:.2f} \approx v_0"

            final_text_str = (
                f"Exit at (x={exit_x_str}, y={exit_y_str}) \\"
                f"Final direction \theta = {angle_str} \\"
                f"{speed_text} \\"
                f"K.E. = \frac{{1}}{{2}} m v_0^2 \text{{ (constant)}}"
            )
            final_text = Tex(final_text_str, font_size=30, tex_environment="{flushleft}")
            final_text.to_corner(UL, buff=0.5)
            final_text.set_background_stroke(color=BLACK, width=3, opacity=0.7) # Add background for readability

            self.play(Write(final_text))

        else:
            # Particle didn't exit as expected
            print("Warning: Particle did not reach y=L or exit calculation failed.")
            no_exit_text = Text("Particle did not reach y=L", color=RED).to_corner(UL)
            self.play(Write(no_exit_text))

        self.wait(3) # Hold final frame
