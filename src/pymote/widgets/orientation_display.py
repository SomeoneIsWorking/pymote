"""
3D Orientation display widget using OpenGL
"""

import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from ..constants import ACCEL_CENTER, ACCEL_1G


class OrientationDisplay(QOpenGLWidget):
    """3D widget to display Wiimote orientation"""
    def __init__(self):
        super().__init__()
        self.accel_x = ACCEL_CENTER
        self.accel_y = ACCEL_CENTER
        self.accel_z = ACCEL_CENTER
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.setMinimumSize(300, 300)
        
    def update_orientation(self, accel_x, accel_y, accel_z):
        """Update orientation from accelerometer using Dolphin's algorithm"""
        self.accel_x = accel_x
        self.accel_y = accel_y
        self.accel_z = accel_z
        
        # Convert raw accelerometer values to normalized acceleration vector
        # Wiimote coordinate system: X+ is left, Y+ is forward (toward buttons), Z+ is up
        # Raw values: ~512 is 0g, ~612 is +1g, ~412 is -1g
        ax = (accel_x - ACCEL_CENTER) / ACCEL_1G
        ay = (accel_y - ACCEL_CENTER) / ACCEL_1G
        az = (accel_z - ACCEL_CENTER) / ACCEL_1G
        
        # Normalize the acceleration vector
        accel_length = np.sqrt(ax*ax + ay*ay + az*az)
        if accel_length > 0.01:  # Avoid division by zero
            ax /= accel_length
            ay /= accel_length
            az /= accel_length
            
            # Calculate pitch and roll from normalized acceleration
            # Based on Dolphin's GetPitch and GetRoll functions (Dynamics.cpp:411-421)
            # Pitch: rotation around X axis (forward/backward tilt)
            # Roll: rotation around Y axis (left/right tilt)
            
            # GetPitch: atan2(vec.y, sqrt(vec.x^2 + vec.z^2))
            self.rotation_x = np.arctan2(ay, np.sqrt(ax*ax + az*az)) * 180 / np.pi
            
            # GetRoll: atan2(vec.x, vec.z)
            self.rotation_y = np.arctan2(ax, az) * 180 / np.pi
        
        self.update()
    
    def initializeGL(self):
        """Initialize OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
    
    def resizeGL(self, w, h):
        """Handle resize"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """Render the 3D scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.15, 1.0)
        
        glLoadIdentity()
        glTranslatef(0, 0, -8)
        
        # Apply rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)
        
        # Draw Wiimote-like shape
        self._draw_wiimote()
    
    def _draw_wiimote(self):
        """Draw a simplified Wiimote shape"""
        # Main body (elongated box)
        glColor3f(0.9, 0.9, 0.95)
        
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-0.3, -1.0, 0.2)
        glVertex3f(0.3, -1.0, 0.2)
        glVertex3f(0.3, 1.0, 0.2)
        glVertex3f(-0.3, 1.0, 0.2)
        glEnd()
        
        # Back face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        glVertex3f(-0.3, -1.0, -0.2)
        glVertex3f(-0.3, 1.0, -0.2)
        glVertex3f(0.3, 1.0, -0.2)
        glVertex3f(0.3, -1.0, -0.2)
        glEnd()
        
        # Sides
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        glVertex3f(0.3, -1.0, -0.2)
        glVertex3f(0.3, 1.0, -0.2)
        glVertex3f(0.3, 1.0, 0.2)
        glVertex3f(0.3, -1.0, 0.2)
        glEnd()
        
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.3, -1.0, -0.2)
        glVertex3f(-0.3, -1.0, 0.2)
        glVertex3f(-0.3, 1.0, 0.2)
        glVertex3f(-0.3, 1.0, -0.2)
        glEnd()
        
        # Top
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(-0.3, 1.0, -0.2)
        glVertex3f(-0.3, 1.0, 0.2)
        glVertex3f(0.3, 1.0, 0.2)
        glVertex3f(0.3, 1.0, -0.2)
        glEnd()
        
        # Bottom
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glVertex3f(-0.3, -1.0, -0.2)
        glVertex3f(0.3, -1.0, -0.2)
        glVertex3f(0.3, -1.0, 0.2)
        glVertex3f(-0.3, -1.0, 0.2)
        glEnd()
        
        # Draw buttons on front
        # A button
        glColor3f(0.2, 0.6, 1.0)
        glPushMatrix()
        glTranslatef(0, 0.2, 0.21)
        self._draw_sphere(0.15, 10, 10)
        glPopMatrix()
        
        # B button (trigger)
        glColor3f(1.0, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0, -0.3, 0.21)
        self._draw_sphere(0.1, 10, 10)
        glPopMatrix()
        
        # D-pad
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0, 0.6, 0.21)
        glScalef(0.3, 0.3, 0.05)
        self._draw_cube()
        glPopMatrix()
        
        # IR camera at top
        glColor3f(0.1, 0.1, 0.2)
        glPushMatrix()
        glTranslatef(0, 0.9, 0.21)
        self._draw_sphere(0.08, 10, 10)
        glPopMatrix()
    
    def _draw_sphere(self, radius, slices, stacks):
        """Draw a sphere"""
        quad = gluNewQuadric()
        gluSphere(quad, radius, slices, stacks)
        gluDeleteQuadric(quad)
    
    def _draw_cube(self):
        """Draw a unit cube"""
        glBegin(GL_QUADS)
        # Front
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Back
        glNormal3f(0, 0, -1)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # Top
        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        # Bottom
        glNormal3f(0, -1, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        # Right
        glNormal3f(1, 0, 0)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        # Left
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glEnd()
