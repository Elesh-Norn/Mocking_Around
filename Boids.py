import random
import arcade
import math

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_BOID = 0.2

BOID_COUNT = 20
MAX_SPEED = 40

MAX_VIEW = 10
MAX_AVOID_FORCE = 10

ATTRACTION_RADIUS = 60
ATTRACTION_FORCE = 10
ALIGNEMENT_RADIUS = 60

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Boids"


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
        self.acc = [1, 1]
        self.ahead = [0, 0]
        # Not used yet
        self.view_radius = 5

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

        self.ahead = [(self.pos[0] + self.vel[0] * MAX_VIEW) % SCREEN_HEIGHT,
                      (self.pos[1] + self.vel[1] * MAX_VIEW) % SCREEN_WIDTH]

        magnitude = self.magnitude(self.pos, self.vel)
        if magnitude > MAX_SPEED or magnitude < 1:
            self.vel = self.normalise(self.vel, magnitude)
            self.vel[0] *= MAX_SPEED
            self.vel[1] *= MAX_SPEED

    def avoidance(self, sprite: arcade.Sprite):
        sprite_pos = [sprite.center_y, sprite.center_x]

        # Look in front
        ahead2 = [self.ahead[0] * 0.5, self.ahead[0] * 0.5]
        ahead_dist = self.toroidal_distance(self.ahead, sprite_pos)
        ahead2_dist = self.toroidal_distance(ahead2, sprite_pos)

        # Collision with player_sprite (width might not be the best)
        if ahead_dist < self.view_radius or ahead2_dist < self.view_radius:
            # Calculate the avoidance force
            avoid_force = [self.ahead[0] - sprite.center_y,
                           self.ahead[1] - sprite.center_x]
            return avoid_force

        return [0, 0]

    def alignement(self, sprite: arcade.Sprite)->list:

        ahead_dist = self.toroidal_distance(self.pos, [sprite.center_y, sprite.center_x])
        if ahead_dist <= ATTRACTION_RADIUS:
            self.view_radius += 1
            return sprite.vel

        return [0, 0]

    def attraction(self, sprite: arcade.Sprite)->list:
        if self.toroidal_distance(self.pos, sprite.pos) <= ATTRACTION_RADIUS:
            return sprite.pos
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
        return math.sqrt(abs(pos1[1]*pos1[0]+pos2[1]*pos2[0]))

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
            random_vel = [random.randrange(-10, 10), random.randrange(-10, 10)]
            boid = Boid("images/char2.png", SPRITE_SCALING_BOID, random_pos,
                        random_vel)
            self.boid_list.append(boid)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.boid_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        pass

    def on_update(self, delta_time):
        """ Movement and game logic """

        for boid in self.boid_list:

            avoid_total = [0, 0]
            attraction_total = [0, 0]
            alignement_total = [0, 0]
            print(boid.vel)

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

            alignement_total[0] = attraction_total[0] / boid.view_radius * MAX_SPEED
            alignement_total[1] = attraction_total[1] / boid.view_radius * MAX_SPEED

            # Normalising
            magnitude = boid.magnitude(boid.vel, avoid_total)
            avoid = boid.normalise(avoid_total, magnitude)

            magnitude = boid.magnitude(boid.vel, alignement_total)
            alignement = boid.normalise(alignement_total, magnitude)

            magnitude = boid.magnitude(boid.vel, attraction_total)
            attraction = boid.normalise(attraction_total, magnitude)

            # Adding Forces
            boid.acc[0] = attraction[0] * ATTRACTION_FORCE \
                          + avoid[0] * MAX_AVOID_FORCE \
                          + alignement[0]
            boid.acc[1] = attraction[1] * ATTRACTION_FORCE \
                          + avoid[1] * MAX_AVOID_FORCE \
                          + alignement[0]
            boid.update()


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
