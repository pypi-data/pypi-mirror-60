import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib import animation
from .physics_engine import Particle, Simulation
from intechinvestments import brand
from intechinvestments.brand import intech_purple, intech_yellow

# Supercollider splash screen simulation
#
# Forked from a project by Christian Hill at https://github.com/xnx/collision
# See Christian's blog post at https://scipython.com/blog/two-dimensional-collisions/



SMALL_RADIUS = 0.01
NUM_PARTICLES = 125
RADIUS_RATIO = 4
LARGE_RADIUS = SMALL_RADIUS*RADIUS_RATIO
LARGE_STYLE  = {'facecolor':intech_yellow,
                'edgecolor': intech_yellow,
                'linewidth': 2,
                'fill': True}
SUN_STYLE    = {'facecolor':intech_yellow,
                'edgecolor': intech_purple,
                'linewidth': 3,
                'fill': None}

MASS_RATIO   = RADIUS_RATIO**2
NUM_LARGE    = 8
SMALL_PARTICLE_MASS = 1.0
LARGE_PARTICLE_MASS = MASS_RATIO*SMALL_PARTICLE_MASS

SUN_RATIO    = 7
SUN_MASS     = 0.01*(SUN_RATIO)*LARGE_PARTICLE_MASS
SUN_RADIUS   = SUN_RATIO*LARGE_RADIUS

#--------------------------------------------------------------------


def show():
    # Simulation similar to splash screen
    nparticles = NUM_PARTICLES
    small_particle_radius = SMALL_RADIUS
    styles = {'facecolor':intech_purple,'edgecolor': intech_purple, 'linewidth': 2, 'fill': True}

    sim = PeriodicSimulation(n=nparticles, radius=small_particle_radius, styles=styles)
    # Despite being bigger, set the mass of the large particle to be the same
    # as the small ones so it gains a bit of momentum in the collisions
    sim.particles[0].mass = SUN_MASS
    sim.particles[0].has_image = True
    for k in range(1,NUM_LARGE+1):
        sim.particles[k].mass = LARGE_PARTICLE_MASS
    for k in range(NUM_LARGE,nparticles):
        try:
            sim.particles[k].mass = SMALL_PARTICLE_MASS
        except:
            pass

    sim.dt = 0.02
    sim.do_animation(save=False)




class PeriodicParticle(Particle):
    def overlaps(self, other):
        """Does the circle of this Particle overlap that of other?"""

        total = 0.
        dx = abs(self.x - other.x)
        dx = min(dx, 1-dx)
        dy = abs(self.y - other.y)
        dy = min(dy, 1-dy)
        return np.hypot(dx, dy) < self.radius + other.radius

    def draw(self, ax):
        """Add this Particle's Circle patch to the Matplotlib Axes ax."""

        circle = Circle(xy=self.r, radius=self.radius, **self.styles)
        ax.add_patch(circle)

        if self.x + self.radius > 1:
            ax.add_patch(Circle(xy=(self.x-1, self.y),
                                radius=self.radius, **self.styles))
        if self.x - self.radius < 0:
            ax.add_patch(Circle(xy=(1+self.x, self.y),
                                radius=self.radius, **self.styles))
        if self.y + self.radius > 1:
            ax.add_patch(Circle(xy=(self.x, self.y-1),
                                radius=self.radius, **self.styles))
        if self.y - self.radius < 0:
            ax.add_patch(Circle(xy=(self.x, 1+self.y),
                                radius=self.radius, **self.styles))
        return circle

    def advance(self, dt):
        """Advance the Particle's position forward in time by dt."""

        self.x = (self.x + self.vx * dt) % 1
        self.y = (self.y + self.vy * dt) % 1










class PeriodicSimulation(Simulation):
    """A class for a simple hard-circle molecular dynamics simulation.

    The simulation is carried out on a square domain: 0 <= x < 1, 0 <= y < 1.

    """

    ParticleClass = PeriodicParticle

    def init_particles(self, n, radius, styles ):
        self.n = n
        # First place the larger particles
        p0 = self.ParticleClass(x=0.5, y=0.5, vx=0, vy=0, radius=SUN_RADIUS, styles=SUN_STYLE )
        self.particles = [p0, ]


        for _ in range(NUM_LARGE):
            while not self.place_particle(LARGE_RADIUS, LARGE_STYLE):
                pass


        # Now place the other, smaller, moving particles.
        for i in range(n-NUM_LARGE-1):
            # Try to find a random initial position for this particle.
            while not self.place_particle(radius, styles):
                pass

    #def handle_boundary_collisions(self, p):
    #    pass

    def advance_animation(self):
        """Advance the animation by self.dt."""

        # Blitting would be a bit complicated because circle patches come and
        # go as a circle crosses the periodic boundaries, so we make life
        # easy for ourselves and redraw the whole Axes object for each frame.
        self.advance()
        self.ax.clear()
        self.ax.xaxis.set_ticks([])
        self.ax.yaxis.set_ticks([])
        for particle in self.particles:
            particle.draw(self.ax)
        return

    def do_animation(self, save=False, filename='collision.mp4'):
        """Set up and carry out the animation of the molecular dynamics."""

        self.setup_animation()
        self.init()
        anim = animation.FuncAnimation(self.fig, self.animate,
                               frames=100, interval=1, blit=False)
        self.save_or_show_animation(anim, save, filename)





if __name__ == '__main__':
    show_intech_splash()
