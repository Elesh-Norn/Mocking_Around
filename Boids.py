import random
import arcade
import math
import numpy

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_BOID = 0.2

BOID_COUNT = 20
MAX_SPEED = 5
MAX_VIEW = 10

AVOID_RADIUS = 30
AVOID_FORCE = 1

ATTRACTION_RADIUS = 50
ATTRACTION_FORCE = 10

ALIGNEMENT_RADIUS = 200
ALIGNEMENT_FORCE = 10

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Boids"

BOID = True


class Boid(arcade.Sprite):
    """
    This class represents the  Boids on our screen. It is a child class of
    the arcade library's "Sprite" class.
    """

    def __init__(self, image_path, scaling,
                 pos: list, vel: list):

        super().__init__(image_path, scaling)
        self.pos = pos
        self.vel = vel
        self.angle += -90
        self.previous_vel = self.vel
        self.acc = [0, 0]
        self.ahead = [0, 0]
        self.frame = 0


    def calculate_sprite_roation_angle(self):
        v1 = self.vel / numpy.linalg.norm(self.vel)
        v2 = self.previous_vel / numpy.linalg.norm(self.previous_vel)
        angle = numpy.arccos(numpy.clip(numpy.dot(v1, v2), -1.0, 1.0))*57.296
        direction = self.vel[0]*self.previous_vel[1] - self.vel[1]*self.previous_vel[0]
        if direction > 0:
            return angle
        elif direction < 0:
            return -angle
        return 0

    def update(self):

        # Update the position
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # Pacman thing
        self.pos[0] = self.pos[0] % SCREEN_HEIGHT
        self.pos[1] = self.pos[1] % SCREEN_WIDTH

        # Accelerate
        self.vel[0] += self.acc[0]
        self.vel[1] += self.acc[1]

        # Actually modify the sprite position
        self.center_x = self.pos[1]
        self.center_y = self.pos[0]

        self.ahead = [(self.pos[0] + self.vel[0]) % SCREEN_HEIGHT,
                      (self.pos[1] + self.vel[1]) % SCREEN_WIDTH]

        norm = numpy.linalg.norm(self.vel)
        if norm != 0:
            self.vel = self.vel / norm
            self.vel[0] *= MAX_SPEED
            self.vel[1] *= MAX_SPEED

        self.frame += 1
        if self.frame == 10:
            self.angle -= self.calculate_sprite_roation_angle()
            self.previous_vel = self.vel
            self.frame = 0


    def avoidance(self, sprite)->list:
        sprite_pos = [sprite.center_y, sprite.center_x]

        # Look in front
        ahead2 = [self.ahead[0] * 1.5 % SCREEN_HEIGHT, self.ahead[1] * 1.5 % SCREEN_WIDTH]
        ahead_dist = self.toroidal_distance(self.ahead, sprite_pos)
        ahead2_dist = self.toroidal_distance(ahead2, sprite_pos)

        # Collision with player_sprite (width might not be the best)
        if ahead_dist < AVOID_RADIUS or ahead2_dist < AVOID_RADIUS:
            # Calculate the avoidance force
            avoid_force = [self.ahead[0] - sprite.center_y,
                           self.ahead[1] - sprite.center_x]
            return avoid_force

        return [0, 0]

    def alignement(self, sprite)->list:

        dist = self.toroidal_distance(self.pos, [sprite.center_y, sprite.center_x])
        if dist <= ALIGNEMENT_RADIUS:
            return [sprite.ahead[0] - self.pos[0], sprite.ahead[1] - self.pos[1]]

        return [0, 0]

    def attraction(self, sprite)->list:
        if self.toroidal_distance(self.pos, sprite.pos) <= ATTRACTION_RADIUS:
            return [sprite.pos[0] - self.pos[0], sprite.pos[1] - self.pos[1]]
        return [0, 0]

    def euclidian_distance(self, pos1: list, pos2: list)->float:
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def toroidal_distance(self, pos1: list, pos2: list)->float:
        diff_x = abs(pos1[1] - pos2[1])
        diff_y = abs(pos1[0] - pos2[0])

        if diff_x > 0.5:
            diff_x = 1.0 - diff_x

        if diff_y > 0.5:
            diff_y = 1.0 - diff_y

        return math.sqrt(diff_x**2 + diff_y**2)

    def magnitude(self, pos1: list, pos2: list)->float:
        return numpy.sqrt(pos1[1]*pos1[0] - pos2[1]*pos2[0])

    def normalise(self, pos, magnitude: float)->list:
        if magnitude > 0:
            return [pos[0]/magnitude, pos[1]/magnitude]
        return pos


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.boid_list = None

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.BLUEBERRY)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists

        self.boid_list = arcade.SpriteList()


        # Create the boids
        for i in range(BOID_COUNT):

            random_pos = [random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT)]
            random_vel = [random.randrange(-30, 30), random.randrange(-30, 30)]
            boid = Boid("images/char2.png", SPRITE_SCALING_BOID, random_pos,
                        random_vel)
            self.boid_list.append(boid)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.boid_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        pass

    def on_update(self, delta_time):
        """ Movement and game logic """

        for boid in self.boid_list:

            avoid_total = [0, 0]
            attraction_total = [0, 0]
            alignement_total = [0, 0]

            if BOID:
                for boid2 in self.boid_list:
                    if boid2 is not boid:

                        # Compute 1 avoid
                        avoid_force = boid.avoidance(boid2)
                        avoid_total[0] += avoid_force[0]
                        avoid_total[1] += avoid_force[1]

                        # Compute 1 attraction
                        attraction_force = boid.attraction(boid2)
                        attraction_total[0] += attraction_force[0]
                        attraction_total[1] += attraction_force[1]

                        # Compute 1 alignment
                        alignement_force = boid.attraction(boid2)
                        alignement_total[0] += alignement_force[0]
                        alignement_total[1] += alignement_force[1]



                # Normalising
                attraction = [0, 0]
                alignement = [0, 0]
                avoid = [0, 0]
                norm = numpy.linalg.norm(avoid_total)
                if norm != 0:
                    avoid = avoid_total / norm

                norm = numpy.linalg.norm(attraction)
                if norm != 0:
                    attraction = attraction/ norm

                norm = numpy.linalg.norm(alignement)
                if norm != 0:
                    alignement = alignement / norm


                # Adding Forces
                boid.acc[0] = attraction[0] * ATTRACTION_FORCE \
                              + avoid[0] * AVOID_FORCE \
                              + alignement[0] * ALIGNEMENT_FORCE
                boid.acc[1] = attraction[1] * ATTRACTION_FORCE \
                              + avoid[1] * AVOID_FORCE \
                              + alignement[0] * ALIGNEMENT_FORCE
            boid.update()


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
