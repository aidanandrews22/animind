
from manim import *
import math

class RollingBallOnInclinedPlane(Scene):
    def construct(self):
        # Scene parameters
        angle = 30 * DEGREES
        g = 9.8
        # Acceleration for rolling without slipping: a = (5/7) * g * sin(theta)
        acceleration_mag = (5 / 7) * g * math.sin(angle)
        plane_length = 5 # Shorter plane length
        total_time = math.sqrt(2 * plane_length / acceleration_mag) # Time to reach the bottom: s = 0.5*a*t^2 -> t = sqrt(2s/a)
        mid_time = total_time / 2

        # Setup plane
        plane = Line(
            start=LEFT * plane_length / 2,
            end=RIGHT * plane_length / 2,
            stroke_width=6,
            color=WHITE
        ).shift(DOWN*1.5) # Adjusted shift for shorter plane
        plane.rotate(-angle, about_point=plane.get_center())
        plane_start_coord = plane.get_start()
        plane_end_coord = plane.get_end()
        
        # Angle Arc and Label
        angle_arc = Arc(
            radius=0.8, # Slightly smaller radius
            start_angle=plane.get_angle(),
            angle=-angle,
            arc_center=plane_end_coord
        )
        angle_label = MathTex(r"30^\circ", font_size=30).next_to(angle_arc, RIGHT, buff=0.1)
        
        # Ground line
        ground = Line(plane_end_coord + LEFT*0.5, plane_end_coord + RIGHT*1.5, color=GRAY)

        self.play(Create(plane), Create(ground), Create(angle_arc), Write(angle_label))
        self.wait(0.5) # Corresponds to "We start with a simple inclined plane..."

        # Setup ball
        ball_radius = 0.25 # Slightly smaller ball
        ball = Circle(radius=ball_radius, color=RED, fill_opacity=1).move_to(plane_start_coord + UP * ball_radius) # Position ball at the top
        
        self.play(FadeIn(ball)) # Corresponds to "At the top... sits a small red ball..."
        self.wait(0.5)

        # Time tracker for animation
        time = ValueTracker(0)

        # Ball position updater
        def get_ball_position(t):
            distance = 0.5 * acceleration_mag * t**2
            unit_vector = normalize(plane_end_coord - plane_start_coord)
            position_on_line = plane_start_coord + distance * unit_vector
            perp_vector = rotate_vector(unit_vector, 90 * DEGREES)
            return position_on_line + perp_vector * ball_radius

        ball.add_updater(lambda m: m.move_to(get_ball_position(time.get_value())))

        # Velocity vector (with fix for zero-dimension error)
        plane_direction = normalize(plane_end_coord - plane_start_coord)
        epsilon = 1e-6 # Small non-zero value for initial length
        velocity_vector = Arrow(
            start=ball.get_center(),
            end=ball.get_center() + plane_direction * epsilon, # Tiny initial length
            color=BLUE,
            buff=0,
            max_tip_length_to_length_ratio=0.3, # Adjust tip size
            max_stroke_width_to_length_ratio=3   # Adjust stroke width
        )
        velocity_vector.add_updater(
            lambda v: v.put_start_and_end_on(
                start=ball.get_center(),
                end=ball.get_center() + plane_direction * acceleration_mag * time.get_value() * 0.3 # Scaled length
            ) if time.get_value() > 1e-6 else v.put_start_and_end_on(ball.get_center(), ball.get_center() + plane_direction * epsilon) # Keep tiny length if time is near zero
        )

        # Acceleration vector
        acceleration_vector = Arrow(
            start=ball.get_center(),
            end=ball.get_center() + plane_direction * acceleration_mag * 0.3, # Constant length/direction
            color=GREEN,
            buff=0,
            max_tip_length_to_length_ratio=0.3,
            max_stroke_width_to_length_ratio=3
        )
        acceleration_vector.add_updater(
             lambda a: a.put_start_and_end_on(
                 start=ball.get_center(),
                 end=ball.get_center() + plane_direction * acceleration_mag * 0.3
             )
        )

        self.play(FadeIn(velocity_vector), FadeIn(acceleration_vector)) # Introduce vectors
        self.wait(0.2) # Corresponds to "As time begins..." + vectors appearing

        # --- Animation Part 1: Roll to Midpoint ---
        run_time_part1 = mid_time * 1.8 # Adjust speed/duration if needed
        self.play(
            time.animate.set_value(mid_time),
            run_time=run_time_part1, 
            rate_func=linear
        )
        # Corresponds to "...ball rolls down... accelerating. Velocity vectors... blue... Acceleration vectors... green..."

        # --- Freeze and Show Forces ---
        self.wait(0.5) # Freeze time
        velocity_vector.clear_updaters()
        acceleration_vector.clear_updaters()
        ball.clear_updaters() # Freeze ball position

        # Force vectors (at mid_time position)
        ball_center_mid = get_ball_position(mid_time)
        force_scale = 0.8 # Scale factor for force arrows
        gravity_force = Arrow(ball_center_mid, ball_center_mid + DOWN * 1.5 * force_scale, color=YELLOW, buff=0)
        gravity_label = MathTex(r"\vec{F}_g", color=YELLOW, font_size=30).next_to(gravity_force.get_end(), DOWN, buff=0.1)

        normal_force_dir = rotate_vector(plane_direction, 90 * DEGREES)
        normal_force = Arrow(ball_center_mid, ball_center_mid + normal_force_dir * 1.5 * math.cos(angle) * force_scale, color=ORANGE, buff=0) # Magnitude mg*cos(theta) scaled
        normal_label = MathTex(r"\vec{F}_N", color=ORANGE, font_size=30).next_to(normal_force.get_end(), normal_force_dir, buff=0.1)

        friction_force_dir = -plane_direction
        # Rolling friction F_f = (2/7)mg*sin(theta)
        friction_mag_scale = 1.5 * (2/7) * math.sin(angle) * force_scale # Relative scale
        friction_force = Arrow(ball_center_mid, ball_center_mid + friction_force_dir * friction_mag_scale, color=PURPLE, buff=0)
        friction_label = MathTex(r"\vec{F}_f", color=PURPLE, font_size=30).next_to(friction_force.get_end(), friction_force_dir, buff=0.1)

        forces = VGroup(gravity_force, normal_force, friction_force)
        labels = VGroup(gravity_label, normal_label, friction_label)
        
        self.play(
            FadeOut(velocity_vector),
            FadeOut(acceleration_vector),
            FadeIn(forces),
            FadeIn(labels)
        )
        self.wait(2.5) # Hold frame showing forces

        # --- Resume Animation ---
        self.play(
            FadeOut(forces),
            FadeOut(labels),
            FadeIn(velocity_vector),
            FadeIn(acceleration_vector)
        )
        
        # Re-add updaters
        ball.add_updater(lambda m: m.move_to(get_ball_position(time.get_value())))
        velocity_vector.add_updater(
             lambda v: v.put_start_and_end_on(
                 start=ball.get_center(),
                 end=ball.get_center() + plane_direction * acceleration_mag * time.get_value() * 0.3
             ) if time.get_value() > 1e-6 else v.put_start_and_end_on(ball.get_center(), ball.get_center() + plane_direction * epsilon)
        )
        acceleration_vector.add_updater(
             lambda a: a.put_start_and_end_on(
                 start=ball.get_center(),
                 end=ball.get_center() + plane_direction * acceleration_mag * 0.3
             )
        )

        self.wait(0.5) # Corresponds to "The animation resumes..."

        # --- Animation Part 2: Roll to Bottom ---
        run_time_part2 = (total_time - mid_time) * 1.8 # Adjust speed/duration
        self.play(
            time.animate.set_value(total_time),
            run_time=run_time_part2, 
            rate_func=linear
        )

        # Clear updaters for final state
        ball.clear_updaters()
        velocity_vector.clear_updaters()
        acceleration_vector.clear_updaters()

        self.play(FadeOut(velocity_vector), FadeOut(acceleration_vector), run_time=0.5)
        
        self.wait(1.5) # Final pause

