"""
Sprite Follow Player 2

This calculates a 'vector' towards the player and randomly updates it based
on the player's location. This is a bit more complex, but more interesting
way of following the player.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_follow_simple_2
"""

import random
import arcade
import math

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_BOID = 0.2
BOID_COUNT = 30
MAX_SPEED = 3
MAX_VIEW = 20

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Boides"

SPRITE_SPEED = 0.5


class Boid(arcade.Sprite):
    """
    This class represents the  Boids on our screen. It is a child class of
    the arcade library's "Sprite" class.
    """

    def __init__(self, image_path, scaling,
                 pos: list, vel: list,
                 acc: float, view_radius=50):

        super().__init__(image_path, scaling)
        self.pos = pos
        self.vel = vel
        self.acc = acc
        # Not used yet
        self.view_radius = view_radius

    def update(self):
        # Update the position
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # Pacman thing
        self.pos[0] = self.pos[0] % SCREEN_HEIGHT
        self.pos[1] = self.pos[1] % SCREEN_WIDTH

        # Trying to normalize speed
        maxi = max(self.vel)
        if maxi > 0 or maxi < 0:
            self.vel[0] = self.vel[0] / maxi * MAX_SPEED
            self.vel[1] = self.vel[1] / maxi * MAX_SPEED

        # Actually modify the sprite position
        self.center_x = self.pos[1]
        self.center_y = self.pos[0]

    def avoidance(self, player_sprite: arcade.Sprite):
        # For now, avoid the player sprite

        player_pos = [player_sprite.center_y, player_sprite.center_x]

        # Look in front
        ahead = [self.pos[0] + self.vel[0] * MAX_VIEW,
                 self.pos[1] + self.vel[1] * MAX_VIEW]
        ahead2 = [ahead[0] * 0.5, ahead[0] * 0.5]
        ahead_dist = self.euclidian_distance(ahead, player_pos)
        ahead2_dist = self.euclidian_distance(ahead2, player_pos)

        # Collision with player_sprite (width might not be the best)
        if ahead_dist < player_sprite.width or ahead2_dist < player_sprite.width:
            # Calculate the avoidance force
            avoid_force = [ahead[0] - player_sprite.center_y,
                           ahead[1] - player_sprite.center_x]

            # Trying to normalise
            maxi = max(avoid_force)  # What if negative ?
            if maxi > 0 or maxi < 0:  # Avoid the 0 division
                avoid_force[0] = avoid_force[0]/maxi * 2
                avoid_force[1] = avoid_force[1] / maxi * 2
                return avoid_force
            else:
                return [0, 0]
        return [0, 0]

    def euclidian_distance(self, pos1: list, pos2: list)->float:
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.player_list = None
        self.boid_list = None

        # Set up the player info
        self.player_sprite = None

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.DEEP_SKY_BLUE)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.boid_list = arcade.SpriteList()

        # Set up the player

        self.player_sprite = arcade.Sprite("images/character.png", SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Create the boids
        for i in range(BOID_COUNT):

            random_pos = [random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT)]
            random_vel = [random.randrange(-10, 10)/10, random.randrange(-10, 10)/10]
            boid = Boid("images/coin_01.png", SPRITE_SCALING_BOID, random_pos,
                        random_vel, 0.1)
            self.boid_list.append(boid)

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.boid_list.draw()
        self.player_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def on_update(self, delta_time):
        """ Movement and game logic """

        for coin in self.boid_list:
            avoid = coin.steering_vel(self.player_sprite)
            if avoid[0] == 0 and avoid[1] == 0:
                coin.vel[0] *= 0.7
                coin.vel[1] *= 0.7
            coin.vel[0] += avoid[0]
            coin.vel[1] += avoid[1]
            coin.update()


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
