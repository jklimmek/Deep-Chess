import chess
import logging
import numpy as np
import torch


def get_logging_config():
    """Configures the logging module."""
    
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s: %(message)s", 
        level=logging.INFO, 
        datefmt="%I:%M:%S"
    )


def seed_everything(seed):
    """Sets the random seed for numpy and torch.

    Args:
        seed (int): The random seed.
    """

    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def write_txt(txt, path):
    """Writes a list of strings to a text file.

    Args:
        txt (list): A list of strings.
        path (str): The path to the text file.
    """

    with open(path, "w") as f:
        for line in txt:
            f.write(line + "\n")


def read_txt(path):
    """Reads a text file and returns a list of strings.

    Args:
        path (str): The path to the text file.

    Returns:
        list: A list of strings.
    """

    with open(path, "r") as f:
        return [line.strip() for line in f.readlines()]


def save_state_dict(name, model, optimizer=None, scheduler=None, train_loss=None, dev_loss=None, 
                    train_accuracy=None, dev_accuracy=None, epoch_idx=None, train_loss_idx=None):
    """Saves the model state dictionary.

    Args:
        model (torch.nn.Module): The model.
        optimizer (torch.optim.Optimizer): The optimizer.
        scheduler (torch.optim.lr_scheduler._LRScheduler): The scheduler.
        train_loss (float): The training loss.
        dev_loss (float): The dev loss.
        train_accuracy (float): The training accuracy.
        dev_accuracy (float): The dev accuracy.
        epoch_idx (int): The epoch index.
        train_loss_idx (int): The train loss index.
    """

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict() if optimizer is not None else None,
            "scheduler_state_dict": scheduler.state_dict() if optimizer is not None else None,
            "train_loss": train_loss if optimizer is not None else None,
            "dev_loss": dev_loss if optimizer is not None else None,
            "train_accuracy": train_accuracy if optimizer is not None else None,
            "dev_accuracy": dev_accuracy if optimizer is not None else None,
            "epoch_idx": epoch_idx if optimizer is not None else None,
            "train_loss_idx": train_loss_idx if optimizer is not None else None,
        },
        name
    )


def load_state_dict(name, model, optimizer=None, scheduler=None):
    """Loads the model state dictionary.

    Args:
        model (torch.nn.Module): The model.
        optimizer (torch.optim.Optimizer): The optimizer.
        scheduler (torch.optim.lr_scheduler._LRScheduler): The scheduler.

    Returns:
        float: The training loss.
        float: The dev loss.
        float: The training accuracy.
        float: The dev accuracy.
        int: The epoch index.
        int: The train loss index.
    """

    checkpoint = torch.load(name)
    model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    if scheduler is not None:
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        
    train_loss = checkpoint.get("train_loss", None)
    dev_loss = checkpoint.get("dev_loss", None)
    train_accuracy = checkpoint.get("train_accuracy", None)
    dev_accuracy = checkpoint.get("dev_accuracy", None)
    epoch_idx = checkpoint.get("epoch_idx", None)
    train_loss_idx = checkpoint.get("train_loss_idx", None)
    return train_loss, dev_loss, train_accuracy, dev_accuracy, epoch_idx, train_loss_idx
    

def fen_to_array(board):
    """Converts a FEN string to a numpy array representation of the chess board.
    
    Each position is converted as binary array of size 773.
    The first 768 positions represent the board (8x8x12).
    The next position represents which side is to move (1 = white, 0 = black).
    The last 4 positions represent the castling rights (KQkq).

    Args:
        board (str or chess.Board): The FEN string or the chess board.

    Returns:
        numpy.ndarray: A numpy array representation of the chess board.
    """

    # Initialize the board and the arrays of piece types and colors.
    board = chess.Board(board) if isinstance(board, str) else board
    piece_types = [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING]
    colors = [chess.WHITE, chess.BLACK]

    # Create an array for each piece type and color.
    pieces = []
    
    # Loop through the piece types and colors and add the pieces to the arrays.
    for color in colors:
        for piece_type in piece_types:

            # Convert the board pieces to a numpy array.
            piece_array = np.asarray(board.pieces(piece_type, color).tolist(), dtype=int)

            # Add the piece array to the list of piece arrays.
            pieces.append(piece_array)

    # Add the side to move to the array.
    side_to_move = np.array([int(board.turn)], dtype=int)

    # Add the castling rights to the array.
    castling_rights = np.array([
        int(board.has_kingside_castling_rights(chess.WHITE)),
        int(board.has_queenside_castling_rights(chess.WHITE)),
        int(board.has_kingside_castling_rights(chess.BLACK)),
        int(board.has_queenside_castling_rights(chess.BLACK)),
    ], dtype=int)

    # Concatenate the arrays.
    result = np.concatenate(pieces + [side_to_move, castling_rights])

    # Return the result.
    return result


def array_to_fen(array):
    """Converts a numpy array representation of a chess board to a FEN string.

    This is the inverse of the fen_to_array function.
    First 768 positions represent the board (8x8x12).
    Next position represents which side is to move (1 = white, 0 = black).
    Last 4 positions represent the castling rights (KQkq).

    Args:
        array (numpy.ndarray): A numpy array representation of a chess board.

    Returns:
        str: The FEN string representing the chess board.
    """

    # Initialize the board and the arrays of piece types and colors.
    # Board is initialized with no pieces.
    piece_types = [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING]
    colors = [chess.WHITE, chess.BLACK]
    board = chess.Board(fen=None)

    # Set the pieces on the board.
    index = 0
    for color in colors:
        for piece_type in piece_types:

            # Convert the piece array to a 2D array.
            piece_array = array[index : index + 64].reshape(8, 8)

            # Loop through the 2D array and set the pieces on the board.
            for i, row in enumerate(piece_array):
                for j, piece in enumerate(row):

                    # Convert the 2D array to a square index.
                    square_index = i * 8 + j

                    # Set the piece on the board.
                    if piece:
                        board.set_piece_at(square_index, chess.Piece(piece_type, color))

            # Increment the index.
            index += 64

    # Set the side to move.
    board.turn = bool(array[index])

    # Set the castling rights.
    board.clean_castling_rights()
    board.set_castling_fen(
        "".join(
            [
                "K" if array[index + 1] else "",
                "Q" if array[index + 2] else "",
                "k" if array[index + 3] else "",
                "q" if array[index + 4] else "",
            ]
        )
    )

    # Return the FEN string.
    return board.fen()