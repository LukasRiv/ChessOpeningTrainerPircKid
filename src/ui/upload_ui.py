"""UI for uploading chess files (screenshots, PGN, FEN).

This module provides the UploadUI class to handle file uploads with tabs
for different file types (screenshots, PGN, FEN).
"""

import os
import pygame
from src.ui.constants import (
    BOARD_SIZE, SIDEBAR_WIDTH, WINDOW_HEIGHT,
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_TEXT_COLOR,
    BUTTON_BORDER_COLOR, BUTTON_BORDER_RADIUS, WHITE
)
import tkinter as tk
from tkinter import filedialog

class UploadUI:
    """Handles the upload interface for chess files with tabbed navigation.

    Attributes:
        chess_ui (ChessUI): Reference to the main ChessUI instance.
        visible (bool): Whether the upload UI is currently visible.
        active_tab (str): Current active tab ("Screenshot", "PGN", or "FEN").
        upload_area_rect (pygame.Rect): Rectangle for the drag-and-drop area.
        load_button_rect (pygame.Rect): Rectangle for the Load button.
        file_path (str | None): Path to the selected file.
        tabs (list[str]): List of available tabs.
    """

    def __init__(self, chess_ui) -> None:
        """Initialize the Upload UI.

        Args:
            chess_ui (ChessUI): Reference to the main ChessUI instance.
        """
        self.chess_ui = chess_ui
        self.visible = False
        self.active_tab = "PGN"  # Default tab
        self.file_path = None
        self.tabs = ["Screenshot", "PGN", "FEN"]

        # Calculate dimensions
        self.upload_width = SIDEBAR_WIDTH - 40
        self.upload_height = 300
        self.upload_x = BOARD_SIZE + 20
        self.upload_y = 0  # Will be set in show()

        # Upload area (drag-and-drop)
        self.upload_area_rect = pygame.Rect(
            self.upload_x,
            100,  # Will be set in show()
            self.upload_width,
            self.upload_height - 150
        )

        # Load button
        self.load_button_rect = pygame.Rect(
            self.upload_x + (self.upload_width - 100) // 2,
            0,  # Will be set in show()
            100,
            30
        )

    def show(self, y_position: int = None) -> None:
        """Show the upload UI at a specific Y position.

        Args:
            y_position (int): Y coordinate to position the upload UI.
        """
        self.visible = True
        self.file_path = None
        self.active_tab = "PGN"  # Reset to default tab

        # Set Y position
        if y_position is not None:
            self.upload_y = y_position

        # Recalculate dependent rectangles
        self.upload_area_rect.y = self.upload_y + 100
        self.load_button_rect.y = self.upload_y + self.upload_height - 40

    def hide(self) -> None:
        """Hide the upload UI."""
        self.visible = False
        self.file_path = None

    def handle_click(self, pos: tuple[int, int]) -> None:
        """Handle mouse clicks on the upload UI.

        Args:
            pos (tuple[int, int]): Mouse position (x, y).
        """
        if not self.visible:
            return

        # Check tab clicks
        tab_width = self.upload_width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(
                self.upload_x + i * tab_width,
                self.upload_y + 50,  # Below title
                tab_width,
                40
            )
            if tab_rect.collidepoint(pos):
                self.active_tab = tab
                return

        # Check upload area click (simulate file selection)
        if self.upload_area_rect.collidepoint(pos):
            self._open_file_dialog()
            return

        # Check Load button click
        if self.load_button_rect.collidepoint(pos) and self.file_path:
            self._load_file()
            return

    def _load_file(self) -> None:
        """Load the selected file based on the active tab."""
        if not self.file_path:
            self.chess_ui._show_error("No file selected!")
            return

        if self.active_tab == "Screenshot":
            self.chess_ui._show_error("Screenshot import: Not implemented yet!")
        elif self.active_tab == "PGN":
            try:
                self.chess_ui.opening_trainer_ui.load_opening(self.file_path)
                self.chess_ui.current_opening_name = os.path.basename(self.file_path)
                self.chess_ui.game_mode = "opening_training"
                self.chess_ui.interaction_enabled = True
                self.hide()
                self.chess_ui.menu_manager._update_button_visibility()
            except Exception as e:
                self.chess_ui._show_error(f"Failed to load PGN: {e}")
        elif self.active_tab == "FEN":
            self.chess_ui._show_error("FEN import: Not implemented yet!")

    def _open_file_dialog(self) -> None:
        """Open a file dialog to select a file based on the active tab."""
        # Crée une fenêtre racine cachée pour le dialogue de fichier
        root = tk.Tk()
        root.withdraw()  # Cache la fenêtre principale

        # Définit les types de fichiers selon l'onglet actif
        file_types = {
            "Screenshot": [("Image files", "*.png *.jpg *.jpeg")],
            "PGN": [("PGN files", "*.pgn")],
            "FEN": [("FEN files", "*.fen *.txt")]
        }

        # Ouvre le dialogue de sélection de fichier
        file_path = filedialog.askopenfilename(
            title=f"Select {self.active_tab} file",
            filetypes=file_types.get(self.active_tab, [])
        )

        # Si un fichier est sélectionné, stocke-le
        if file_path:
            self.file_path = file_path
            print(f"[DEBUG] Selected file: {file_path}")

    def handle_file_drop(self, file_path: str) -> None:
        """Handle a file dropped into the upload area.

        Args:
            file_path (str): Path to the dropped file.
        """
        valid_extensions = {
            "Screenshot": [".png", ".jpg", ".jpeg"],
            "PGN": [".pgn"],
            "FEN": [".fen", ".txt"]
        }

        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in valid_extensions.get(self.active_tab, []):
            self.file_path = file_path
            print(f"[DEBUG] File selected: {file_path}")
        else:
            self.chess_ui._show_error(
                f"Invalid file type for {self.active_tab}. "
                f"Expected: {', '.join(valid_extensions[self.active_tab])}"
            )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the upload UI on the given surface.

        Args:
            surface (pygame.Surface): Pygame surface to draw on.
        """
        if not self.visible:
            return

        # Draw background (same style as sidebar)
        upload_bg_rect = pygame.Rect(
            self.upload_x,
            self.upload_y,
            self.upload_width,
            self.upload_height
        )
        pygame.draw.rect(surface, (30, 30, 30), upload_bg_rect, border_radius=10)

        # Draw title (centered at top)
        font = pygame.font.SysFont("Arial", 20, bold=True)
        title = font.render("Upload Files", True, WHITE)
        title_rect = title.get_rect(
            midtop=(self.upload_x + self.upload_width // 2, self.upload_y + 10)
        )
        surface.blit(title, title_rect)

        # Draw tabs (with consistent styling)
        tab_width = self.upload_width // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_rect = pygame.Rect(
                self.upload_x + i * tab_width,
                self.upload_y + 50,
                tab_width,
                40
            )

            # Use BUTTON_BG_HOVER for active tab, darker for inactive
            tab_color = BUTTON_BG_HOVER if tab == self.active_tab else (40, 40, 40)
            pygame.draw.rect(surface, tab_color, tab_rect, border_radius=5)

            # Draw tab text (brighter for active tab)
            tab_font = pygame.font.SysFont("Arial", 16)
            text_color = WHITE if tab == self.active_tab else (150, 150, 150)
            tab_text = tab_font.render(tab, True, text_color)
            tab_text_rect = tab_text.get_rect(center=tab_rect.center)
            surface.blit(tab_text, tab_text_rect)

        # Draw upload area
        pygame.draw.rect(
            surface,
            (100, 100, 100),
            self.upload_area_rect,
            width=2,
            border_radius=5
        )

        # Draw upload text (centered)
        upload_font = pygame.font.SysFont("Arial", 16)
        upload_text = upload_font.render(
            f"Browse {self.active_tab} Files or drop",
            True,
            (200, 200, 200)
        )
        upload_text_rect = upload_text.get_rect(center=self.upload_area_rect.center)
        surface.blit(upload_text, upload_text_rect)

        # Draw file type hint (smaller, below)
        hint_font = pygame.font.SysFont("Arial", 12)
        hint_texts = {
            "Screenshot": "(png, jpg, etc)",
            "PGN": "(pgn)",
            "FEN": "(fen, txt)"
        }
        hint_text = hint_font.render(hint_texts[self.active_tab], True, (150, 150, 150))
        hint_rect = hint_text.get_rect(
            center=(self.upload_area_rect.centerx, self.upload_area_rect.centery + 20)
        )
        surface.blit(hint_text, hint_rect)

        # Draw Load button (consistent with other buttons)
        is_hovered = self.load_button_rect.collidepoint(pygame.mouse.get_pos())
        button_color = BUTTON_BG_HOVER if is_hovered else BUTTON_BG
        pygame.draw.rect(
            surface,
            button_color,
            self.load_button_rect,
            border_radius=BUTTON_BORDER_RADIUS
        )
        pygame.draw.rect(
            surface,
            BUTTON_BORDER_COLOR,
            self.load_button_rect,
            width=2,
            border_radius=BUTTON_BORDER_RADIUS
        )

        load_font = pygame.font.SysFont("Arial", 16)
        load_text = load_font.render("Load", True, BUTTON_TEXT_COLOR)
        load_text_rect = load_text.get_rect(center=self.load_button_rect.center)
        surface.blit(load_text, load_text_rect)

        # Draw selected file name if any
        if self.file_path:
            file_font = pygame.font.SysFont("Arial", 12)
            file_text = file_font.render(
                f"Selected: {os.path.basename(self.file_path)}",
                True,
                (200, 200, 200)
            )
            file_rect = file_text.get_rect(
                center=(self.upload_area_rect.centerx, self.upload_area_rect.bottom - 20)
            )
            surface.blit(file_text, file_rect)

    def _draw_dashed_rect(self, surface: pygame.Surface, rect: pygame.Rect, color: tuple) -> None:
        """Draw a dashed rectangle for the upload area.

        Args:
            surface (pygame.Surface): Surface to draw on.
            rect (pygame.Rect): Rectangle to draw as dashed.
            color (tuple): Color of the dashed lines.
        """
        dash_length = 10
        # Top and bottom borders
        for i in range(0, rect.width, dash_length * 2):
            pygame.draw.line(
                surface, color,
                (rect.x + i, rect.y),
                (rect.x + i + dash_length, rect.y),
                width=2
            )
            pygame.draw.line(
                surface, color,
                (rect.x + i, rect.bottom),
                (rect.x + i + dash_length, rect.bottom),
                width=2
            )
        # Left and right borders
        for i in range(0, rect.height, dash_length * 2):
            pygame.draw.line(
                surface, color,
                (rect.x, rect.y + i),
                (rect.x, rect.y + i + dash_length),
                width=2
            )
            pygame.draw.line(
                surface, color,
                (rect.right, rect.y + i),
                (rect.right, rect.y + i + dash_length),
                width=2
            )