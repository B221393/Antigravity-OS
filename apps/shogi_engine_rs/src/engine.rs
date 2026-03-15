use crate::board::{Board, Color, Move, PieceType};
use rand::seq::SliceRandom;
use std::collections::HashMap; // For random.shuffle

pub struct Engine {
    piece_values: HashMap<PieceType, i32>,
}

impl Engine {
    pub fn new() -> Self {
        let mut piece_values = HashMap::new();
        piece_values.insert(PieceType::Hu, 100);
        piece_values.insert(PieceType::Ky, 300);
        piece_values.insert(PieceType::Ke, 400);
        piece_values.insert(PieceType::Gi, 500);
        piece_values.insert(PieceType::Ki, 600);
        piece_values.insert(PieceType::Ka, 800);
        piece_values.insert(PieceType::Hi, 1000);
        piece_values.insert(PieceType::Ou, 15000);
        piece_values.insert(PieceType::To, 700);
        piece_values.insert(PieceType::Ny, 600);
        piece_values.insert(PieceType::Nk, 600);
        piece_values.insert(PieceType::Ng, 600);
        piece_values.insert(PieceType::Um, 1000);
        piece_values.insert(PieceType::Ry, 1200);

        Self { piece_values }
    }

    pub fn evaluate(&self, board: &Board) -> i32 {
        let mut score = 0;

        // On board pieces
        for &p_val in board.squares.iter() {
            if p_val == (PieceType::Empty as u8) {
                continue;
            }

            let p_type = PieceType::type_of(p_val);
            let color = PieceType::color_of(p_val);
            let val = *self.piece_values.get(&p_type).unwrap_or(&0);

            if let Some(c) = color {
                if c == Color::Black {
                    score += val;
                } else {
                    score -= val;
                }
            }
        }

        // Hand pieces
        if let Some(black_hand) = board.hand.get(&Color::Black) {
            for (&p_type, &count) in black_hand.iter() {
                score += (count as i32) * self.piece_values.get(&p_type).unwrap_or(&0) * 11 / 10;
                // 1.1 multiplier
            }
        }
        if let Some(white_hand) = board.hand.get(&Color::White) {
            for (&p_type, &count) in white_hand.iter() {
                score -= (count as i32) * self.piece_values.get(&p_type).unwrap_or(&0) * 11 / 10;
                // 1.1 multiplier
            }
        }

        score
    }

    pub fn go(&self, board: &Board, _time_limit: u64) -> Option<Move> {
        let mut moves = board.generate_moves();
        if moves.is_empty() {
            return None;
        }

        // Shuffle for variety if scores equal
        let mut rng = rand::thread_rng();
        moves.shuffle(&mut rng);

        let mut best_move: Option<Move> = None;
        let mut best_score = if board.turn == Color::Black {
            i32::MIN
        } else {
            i32::MAX
        };

        for mv in moves {
            let new_board = board.make_move(&mv);
            let score = self.evaluate(&new_board);

            if board.turn == Color::Black {
                if score > best_score {
                    best_score = score;
                    best_move = Some(mv);
                }
            } else {
                if score < best_score {
                    best_score = score;
                    best_move = Some(mv);
                }
            }
        }
        best_move
    }
}
