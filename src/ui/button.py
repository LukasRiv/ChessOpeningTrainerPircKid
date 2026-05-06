"""Button class for the chess UI sidebar."""
import os

import pygame
from src.ui.constants import (
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_TEXT_COLOR,
    BUTTON_BORDER_COLOR, BUTTON_BORDER_RADIUS, BUTTON_PADDING, BUTTON_ICON_PADDING
)

class Button:
    """Class to represent a clickable button in the sidebar or on the board.

    Attributes:
        rect (pygame.Rect): The rectangular area of the button.
        text (str): Text to display on the button.
        icon (str | None): Unicode icon to display (e.g., "←", "↻").
        icon_image (pygame.Surface | None): Image icon to display.
        is_hovered (bool): Indicates if the mouse is hovering over the button.
        visible (bool): Indicates if the button is currently visible.
        children (dict | None): Dictionary of child buttons if this is a parent menu item.
    """

    def __init__(self, x: int, y: int, width: int, height: int, text: str = "", icon: str = None, icon_image_path: str = None) -> None:
        """Initialize a button.

        Args:
            x (int): X-coordinate of the button.
            y (int): Y-coordinate of the button.
            width (int): Width of the button.
            height (int): Height of the button.
            text (str): Text to display on the button (default: "").
            icon (str | None): Unicode icon to display (e.g., "←", "↻").
            icon_image_path (str | None): Path to an image icon (e.g., "assets/icons/flip.png").
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.icon_image = None
        self.is_hovered = False
        self.visible = True  # Par défaut, visible (sauf pour les boutons du menu)
        self.children = None

        # Load icon image if path is provided
        if icon_image_path:
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(os.path.dirname((script_dir)))
                full_path = os.path.join(project_root, icon_image_path)
                self.icon_image = pygame.image.load(full_path)
                # Scale icon to fit button (leave 5px padding)
                max_icon_size = min(width, height) - 10
                self.icon_image = pygame.transform.scale(self.icon_image, (max_icon_size, max_icon_size))
            except FileNotFoundError:
                print(f"Warning: Icon image not found at {icon_image_path}")
                self.icon_image = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button on the given surface with Chess.com-like styling.

        Args:
            surface (pygame.Surface): Surface to draw the button on.
        """
        if not self.visible:
            return

        # Draw button background (rounded rectangle)
        color = BUTTON_BG_HOVER if self.is_hovered else BUTTON_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=BUTTON_BORDER_RADIUS)
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.rect, 2, border_radius=BUTTON_BORDER_RADIUS)

        # Draw icon (image or Unicode)
        if self.icon_image:
            icon_rect = self.icon_image.get_rect(center=self.rect.center)
            surface.blit(self.icon_image, icon_rect)
        elif self.icon:
            icon_font = pygame.font.SysFont("Arial", self.rect.height - 10)
            icon_surface = icon_font.render(self.icon, True, BUTTON_TEXT_COLOR)
            icon_rect = icon_surface.get_rect(center=self.rect.center)
            surface.blit(icon_surface, icon_rect)
        else:
            # Draw text if no icon
            font = pygame.font.SysFont("Arial", 18)
            text_surface = font.render(self.text, True, BUTTON_TEXT_COLOR)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

    def check_hover(self, pos: tuple[int, int]) -> bool:
        """Check if the mouse is hovering over the button.

        Args:
            pos (tuple[int, int]): Mouse position (x, y).

        Returns:
            bool: True if the mouse is hovering over the button.
        """
        if not self.visible:
            return False
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos: tuple[int, int], event: pygame.event) -> bool:
        """Check if the button was clicked.

        Args:
            pos (tuple[int, int]): Mouse position (x, y).
            event (pygame.event): The mouse button down event.

        Returns:
            bool: True if the button was clicked.
        """
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False