use num_enum::IntoPrimitive;

use std::collections::HashMap;

#[derive(Debug, PartialEq, Eq, Clone, Copy, IntoPrimitive, Hash)]
#[repr(u8)]
pub enum Color {
    Black = 0,
    White = 1,
}

impl Color {
    pub fn opposite(self) -> Self {
        match self {
            Color::Black => Color::White,
            Color::White => Color::Black,
        }
    }

    pub fn forward_rank_delta(self) -> i8 {
        match self {
            Color::Black => -1,
            Color::White => 1,
        }
    }
}

#[derive(Debug, PartialEq, Eq, Clone, Copy, IntoPrimitive, Hash)]
#[repr(u8)]
pub enum PieceType {
    Empty = 0,
    Hu = 1, // Pawn
    Ky = 2, // Lance
    Ke = 3, // Knight
    Gi = 4, // Silver
    Ki = 5, // Gold
    Ka = 6, // Bishop
    Hi = 7, // Rook
    Ou = 8, // King

    // Promoted pieces
    To = 11,
    Ny = 12,
    Nk = 13,
    Ng = 14,
    Um = 16,
    Ry = 17,
}

impl PieceType {
    pub fn promote(self) -> Self {
        match self {
            PieceType::Hu => PieceType::To,
            PieceType::Ky => PieceType::Ny,
            PieceType::Ke => PieceType::Nk,
            PieceType::Gi => PieceType::Ng,
            PieceType::Ka => PieceType::Um,
            PieceType::Hi => PieceType::Ry,
            _ => self, // King and promoted pieces don't promote further
        }
    }

    pub fn demote(self) -> Self {
        match self {
            PieceType::To => PieceType::Hu,
            PieceType::Ny => PieceType::Ky,
            PieceType::Nk => PieceType::Ke,
            PieceType::Ng => PieceType::Gi,
            PieceType::Um => PieceType::Ka,
            PieceType::Ry => PieceType::Hi,
            _ => self, // Unpromoted pieces and King don't demote
        }
    }

    pub fn make_piece(piece_type: PieceType, color: Color) -> u8 {
        if piece_type == PieceType::Empty {
            return 0;
        }
        let mut piece_val = piece_type as u8;
        if color == Color::White {
            piece_val |= 32; // Bit 5 for White
        }
        piece_val
    }

    pub fn color_of(piece: u8) -> Option<Color> {
        if piece == 0 {
            return None;
        }
        if (piece & 32) != 0 {
            Some(Color::White)
        } else {
            Some(Color::Black)
        }
    }

    pub fn type_of(piece: u8) -> PieceType {
        // Safe conversion from u8 to PieceType, handling unknown values
        match piece & 31 {
            1 => PieceType::Hu,
            2 => PieceType::Ky,
            3 => PieceType::Ke,
            4 => PieceType::Gi,
            5 => PieceType::Ki,
            6 => PieceType::Ka,
            7 => PieceType::Hi,
            8 => PieceType::Ou,
            11 => PieceType::To,
            12 => PieceType::Ny,
            13 => PieceType::Nk,
            14 => PieceType::Ng,
            16 => PieceType::Um,
            17 => PieceType::Ry,
            _ => PieceType::Empty, // Default or unknown
        }
    }

    // Returns true if the rank is in the promotion zone for a given color
    pub fn is_in_promotion_zone(color: Color, rank: u8) -> bool {
        match color {
            Color::Black => rank <= 2, // Ranks 0, 1, 2
            Color::White => rank >= 6, // Ranks 6, 7, 8
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Move {
    pub from_sq: Option<u8>, // 0-80
    pub to_sq: u8,           // 0-80
    pub promote: bool,
    pub is_drop: bool,
    pub drop_piece: Option<PieceType>, // Only for drops
}

impl std::fmt::Display for Move {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.is_drop {
            write!(f, "Drop({:?} to {})", self.drop_piece, self.to_sq)
        } else {
            write!(
                f,
                "Move({:?}->{}{})",
                self.from_sq,
                self.to_sq,
                if self.promote { "+" } else { "" }
            )
        }
    }
}

#[derive(Debug, Clone)]
pub struct Board {
    pub squares: [u8; 81], // Stores PieceType::make_piece result
    pub turn: Color,
    pub hand: HashMap<Color, HashMap<PieceType, u8>>,
    pub move_number: u32,
}

impl Board {
    pub fn new() -> Self {
        let mut hand_black = HashMap::new();
        let mut hand_white = HashMap::new();
        for p_type_val in 1..=7 {
            // HU to HI
            let p_type = PieceType::type_of(p_type_val);
            hand_black.insert(p_type, 0);
            hand_white.insert(p_type, 0);
        }
        let mut hand_map = HashMap::new();
        hand_map.insert(Color::Black, hand_black);
        hand_map.insert(Color::White, hand_white);

        Self {
            squares: [0; 81],
            turn: Color::Black,
            hand: hand_map,
            move_number: 1,
        }
    }

    pub fn clear(&mut self) {
        self.squares.fill(0);
        self.turn = Color::Black;
        // Re-initialize hand counts to 0
        for (_, hand_map) in self.hand.iter_mut() {
            for (_, count) in hand_map.iter_mut() {
                *count = 0;
            }
        }
        self.move_number = 1;
    }

    pub fn set_sfen(&mut self, sfen: &str) -> Result<(), Box<dyn std::error::Error>> {
        self.clear();
        let parts: Vec<&str> = sfen.split_whitespace().collect();
        let board_str = parts[0];
        let turn_str = parts.get(1).unwrap_or(&"b");
        let hand_str = parts.get(2).unwrap_or(&"-");

        // 1. Parse Turn
        self.turn = match *turn_str {
            "b" => Color::Black,
            "w" => Color::White,
            _ => return Err("Invalid turn string in SFEN".into()),
        };

        // 2. Parse Board
        let ranks: Vec<&str> = board_str.split('/').collect();
        let mut sq_idx = 0;

        let char_map: HashMap<char, PieceType> = [
            ('P', PieceType::Hu),
            ('L', PieceType::Ky),
            ('N', PieceType::Ke),
            ('S', PieceType::Gi),
            ('G', PieceType::Ki),
            ('B', PieceType::Ka),
            ('R', PieceType::Hi),
            ('K', PieceType::Ou),
            ('p', PieceType::Hu),
            ('l', PieceType::Ky),
            ('n', PieceType::Ke),
            ('s', PieceType::Gi),
            ('g', PieceType::Ki),
            ('b', PieceType::Ka),
            ('r', PieceType::Hi),
            ('k', PieceType::Ou),
        ]
        .iter()
        .cloned()
        .collect();

        for rank_str in ranks {
            let mut i = 0;
            while i < rank_str.len() {
                let c = rank_str.chars().nth(i).unwrap();
                if c.is_ascii_digit() {
                    let count = c.to_digit(10).unwrap() as usize;
                    for _ in 0..count {
                        self.squares[sq_idx] = PieceType::Empty as u8;
                        sq_idx += 1;
                    }
                } else if c == '+' {
                    i += 1;
                    let c_promoted = rank_str.chars().nth(i).unwrap();
                    let p_type_raw = *char_map
                        .get(&c_promoted)
                        .ok_or("Invalid promoted piece char")?;
                    let p_type = p_type_raw.promote();
                    let color = if c_promoted.is_ascii_uppercase() {
                        Color::Black
                    } else {
                        Color::White
                    };
                    self.squares[sq_idx] = PieceType::make_piece(p_type, color);
                    sq_idx += 1;
                } else {
                    let p_type = *char_map.get(&c).ok_or("Invalid piece char")?;
                    let color = if c.is_ascii_uppercase() {
                        Color::Black
                    } else {
                        Color::White
                    };
                    self.squares[sq_idx] = PieceType::make_piece(p_type, color);
                    sq_idx += 1;
                }
                i += 1;
            }
        }

        // 3. Parse Hand
        if *hand_str != "-" {
            let mut i = 0;
            while i < hand_str.len() {
                let mut count = 1;
                let c = hand_str.chars().nth(i).unwrap();

                if c.is_ascii_digit() {
                    let mut num_str = String::new();
                    let mut j = i;
                    while j < hand_str.len() && hand_str.chars().nth(j).unwrap().is_ascii_digit() {
                        num_str.push(hand_str.chars().nth(j).unwrap());
                        j += 1;
                    }
                    count = num_str.parse::<u8>()?;
                    i = j;
                    // Move past the number, c will be the piece char
                    // The loop increments i again
                }

                let p_type_char = hand_str.chars().nth(i).unwrap(); // Get piece char
                let p_type = *char_map
                    .get(&p_type_char)
                    .ok_or("Invalid hand piece char")?;
                let color = if p_type_char.is_ascii_uppercase() {
                    Color::Black
                } else {
                    Color::White
                };

                *self
                    .hand
                    .get_mut(&color)
                    .ok_or("Hand map missing color")?
                    .get_mut(&p_type)
                    .ok_or("Hand map missing piece type")? += count;
                i += 1;
            }
        }

        Ok(())
    }

    // Helper to convert 0-80 index to (file, rank)
    fn to_file_rank(sq_idx: u8) -> (u8, u8) {
        (sq_idx % 9, sq_idx / 9)
    }

    // Helper to convert (file, rank) to 0-80 index
    fn to_sq_idx(file: u8, rank: u8) -> u8 {
        rank * 9 + file
    }

    // Check if (file, rank) is within board bounds
    fn is_valid_coord(file: i8, rank: i8) -> bool {
        (0..9).contains(&file) && (0..9).contains(&rank)
    }

    pub fn piece_at(&self, file_idx: u8, rank_idx: u8) -> Option<u8> {
        let idx = Self::to_sq_idx(file_idx, rank_idx) as usize;
        if idx < 81 {
            Some(self.squares[idx])
        } else {
            None
        }
    }

    pub fn put_piece(&mut self, file_idx: u8, rank_idx: u8, piece: u8) {
        let idx = Self::to_sq_idx(file_idx, rank_idx) as usize;
        if idx < 81 {
            self.squares[idx] = piece;
        }
    }

    pub fn generate_moves(&self) -> Vec<Move> {
        let mut moves = Vec::new();
        let my_color = self.turn;

        // 1. Drops
        let hand_pieces = self.hand.get(&my_color).unwrap();
        for (&p_type, &count) in hand_pieces.iter() {
            if count > 0 && p_type != PieceType::Ou {
                // King cannot be dropped
                for sq in 0..81 {
                    let (_file, _rank) = Self::to_file_rank(sq);
                    if self.squares[sq as usize] == (PieceType::Empty as u8) {
                        if self._is_legal_drop(sq, p_type) {
                            moves.push(Move {
                                from_sq: None,
                                to_sq: sq,
                                promote: false,
                                is_drop: true,
                                drop_piece: Some(p_type),
                            });
                        }
                    }
                }
            }
        }

        // 2. On-board moves
        for from_idx in 0..81 {
            let piece_val = self.squares[from_idx];
            if piece_val == (PieceType::Empty as u8) {
                continue;
            }
            if PieceType::color_of(piece_val) != Some(my_color) {
                continue;
            }

            let p_type = PieceType::type_of(piece_val);
            self._generate_piece_moves(from_idx as u8, p_type, my_color, &mut moves);
        }

        // TODO: Filter illegal moves (King in check)
        moves
    }

    // --- Helper functions for move generation ---
    fn _is_legal_drop(&self, sq: u8, p_type: PieceType) -> bool {
        // Nifu (Two Pawns) check for Pawn
        if p_type == PieceType::Hu {
            let file_idx = sq % 9;
            for r in 0..9 {
                let p = self.squares[(r * 9 + file_idx) as usize];
                if PieceType::type_of(p) == PieceType::Hu
                    && PieceType::color_of(p) == Some(self.turn)
                {
                    return false; // Nifu
                }
            }
        }

        // Cannot drop if it immediately promotes (no move)
        let rank = sq / 9;
        match p_type {
            PieceType::Hu | PieceType::Ky => {
                if PieceType::is_in_promotion_zone(self.turn.opposite(), rank) {
                    return false;
                }
            }
            PieceType::Ke => {
                let forward_delta = self.turn.forward_rank_delta();
                // Knight moves 2 ranks forward
                if PieceType::is_in_promotion_zone(self.turn.opposite(), rank)
                    || PieceType::is_in_promotion_zone(
                        self.turn.opposite(),
                        (rank as i8 + forward_delta * 2) as u8,
                    )
                {
                    return false;
                }
            }
            _ => {}
        }

        // TODO: Oute check after drop (check if king is in check after this drop)
        true
    }

    fn _generate_piece_moves(
        &self,
        from_idx: u8,
        p_type: PieceType,
        color: Color,
        moves: &mut Vec<Move>,
    ) {
        let (file, rank) = Self::to_file_rank(from_idx);
        let forward_delta = color.forward_rank_delta();

        let mut candidates: Vec<(i8, i8)> = Vec::new(); // (d_file, d_rank)

        match p_type {
            PieceType::Hu => candidates.push((0, forward_delta)),
            PieceType::Ky => {
                self._generate_sliding_moves(from_idx, &[(0, forward_delta)], moves, color, false);
                return;
            }
            PieceType::Ke => {
                candidates.push((-1, forward_delta * 2));
                candidates.push((1, forward_delta * 2));
            }
            PieceType::Gi => {
                candidates.extend_from_slice(&[
                    (0, forward_delta),
                    (-1, forward_delta),
                    (1, forward_delta),
                    (0, -forward_delta),
                    (-1, 0),
                    (1, 0),
                ]);
            }
            PieceType::Ki | PieceType::To | PieceType::Ny | PieceType::Nk | PieceType::Ng => {
                // Gold movement
                candidates.extend_from_slice(&[
                    (0, forward_delta),
                    (-1, forward_delta),
                    (1, forward_delta),
                    (0, -forward_delta),
                    (-1, 0),
                    (1, 0),
                ]);
            }
            PieceType::Ou => {
                candidates.extend_from_slice(&[
                    (0, 1),
                    (0, -1),
                    (1, 0),
                    (-1, 0),
                    (1, 1),
                    (1, -1),
                    (-1, 1),
                    (-1, -1),
                ]);
            }
            PieceType::Ka | PieceType::Um => {
                // Bishop Diagonals
                self._generate_sliding_moves(
                    from_idx,
                    &[(1, 1), (1, -1), (-1, 1), (-1, -1)],
                    moves,
                    color,
                    p_type == PieceType::Um,
                );
                return;
            }
            PieceType::Hi | PieceType::Ry => {
                // Rook Orthogonals
                self._generate_sliding_moves(
                    from_idx,
                    &[(0, 1), (0, -1), (1, 0), (-1, 0)],
                    moves,
                    color,
                    p_type == PieceType::Ry,
                );
                return;
            }
            _ => {} // Empty and other promoted pieces not handled here
        }

        for (df, dr) in candidates {
            let tgt_file_i8 = file as i8 + df;
            let tgt_rank_i8 = rank as i8 + dr;

            if Self::is_valid_coord(tgt_file_i8, tgt_rank_i8) {
                let tgt_idx = Self::to_sq_idx(tgt_file_i8 as u8, tgt_rank_i8 as u8);
                self._add_move_if_valid(from_idx, tgt_idx, moves, color, p_type);
            }
        }
    }

    fn _generate_sliding_moves(
        &self,
        from_idx: u8,
        dirs: &[(i8, i8)],
        moves: &mut Vec<Move>,
        color: Color,
        is_promoted_slider: bool,
    ) {
        let (from_file, from_rank) = Self::to_file_rank(from_idx);

        for &(df, dr) in dirs {
            for dist in 1..9 {
                let tgt_file_i8 = from_file as i8 + (df * dist);
                let tgt_rank_i8 = from_rank as i8 + (dr * dist);

                if Self::is_valid_coord(tgt_file_i8, tgt_rank_i8) {
                    let tgt_idx = Self::to_sq_idx(tgt_file_i8 as u8, tgt_rank_i8 as u8);
                    let p_at_tgt = self.squares[tgt_idx as usize];

                    if p_at_tgt == (PieceType::Empty as u8) {
                        self._append_move(
                            from_idx,
                            tgt_idx,
                            moves,
                            color,
                            PieceType::type_of(self.squares[from_idx as usize]),
                        );
                    } else if PieceType::color_of(p_at_tgt) != Some(color) {
                        self._append_move(
                            from_idx,
                            tgt_idx,
                            moves,
                            color,
                            PieceType::type_of(self.squares[from_idx as usize]),
                        ); // Capture
                        break; // Sliding piece stops after capture
                    } else {
                        break; // Blocked by own piece
                    }
                } else {
                    break; // Out of bounds
                }
            }
        }

        if is_promoted_slider {
            // Promoted sliders (Um, Ry) also have single-step King moves
            let king_moves_dirs =
                if PieceType::type_of(self.squares[from_idx as usize]) == PieceType::Um {
                    vec![(0, 1), (0, -1), (1, 0), (-1, 0)] // Orthogonal for Um (Bishop)
                } else {
                    // Ry (Rook)
                    vec![(1, 1), (1, -1), (-1, 1), (-1, -1)] // Diagonal for Ry (Rook)
                };

            for (df, dr) in king_moves_dirs {
                let tgt_file_i8 = from_file as i8 + df;
                let tgt_rank_i8 = from_rank as i8 + dr;

                if Self::is_valid_coord(tgt_file_i8, tgt_rank_i8) {
                    let tgt_idx = Self::to_sq_idx(tgt_file_i8 as u8, tgt_rank_i8 as u8);
                    // Single step King moves from Python's logic
                    self._add_move_if_valid(
                        from_idx,
                        tgt_idx,
                        moves,
                        color,
                        PieceType::type_of(self.squares[from_idx as usize]),
                    );
                }
            }
        }
    }

    fn _add_move_if_valid(
        &self,
        from_idx: u8,
        to_idx: u8,
        moves: &mut Vec<Move>,
        color: Color,
        p_type: PieceType,
    ) {
        let p_at_tgt = self.squares[to_idx as usize];
        if p_at_tgt == (PieceType::Empty as u8) {
            self._append_move(from_idx, to_idx, moves, color, p_type);
        } else if PieceType::color_of(p_at_tgt) != Some(color) {
            self._append_move(from_idx, to_idx, moves, color, p_type); // Capture
        }
    }

    fn _append_move(
        &self,
        from_idx: u8,
        to_sq: u8,
        moves: &mut Vec<Move>,
        color: Color,
        p_type: PieceType,
    ) {
        let from_rank = from_idx / 9;
        let to_rank = to_sq / 9;

        let can_promote = PieceType::is_in_promotion_zone(color, from_rank)
            || PieceType::is_in_promotion_zone(color, to_rank);

        // Don't append moves that MUST promote but don't.
        let must_promote = match p_type {
            PieceType::Hu | PieceType::Ky => {
                PieceType::is_in_promotion_zone(color.opposite(), to_rank)
            }
            PieceType::Ke => {
                let forward_delta = color.forward_rank_delta();
                PieceType::is_in_promotion_zone(color.opposite(), to_rank)
                    || PieceType::is_in_promotion_zone(
                        color.opposite(),
                        (to_rank as i8 + forward_delta * 2) as u8,
                    )
            }
            _ => false,
        };

        if must_promote {
            // Only append the promoted version if promotion is forced
            moves.push(Move {
                from_sq: Some(from_idx),
                to_sq,
                promote: true,
                is_drop: false,
                drop_piece: None,
            });
        } else {
            // Append non-promoted move
            moves.push(Move {
                from_sq: Some(from_idx),
                to_sq,
                promote: false,
                is_drop: false,
                drop_piece: None,
            });
            // If promotion is optional and possible, append promoted move as well
            if can_promote
                && p_type != PieceType::Ou
                && p_type != PieceType::Ki
                && (p_type as u8) < (PieceType::To as u8)
            {
                moves.push(Move {
                    from_sq: Some(from_idx),
                    to_sq,
                    promote: true,
                    is_drop: false,
                    drop_piece: None,
                });
            }
        }
    }

    pub fn make_move(&self, mv: &Move) -> Self {
        let mut new_board = self.clone(); // Clone the current board

        // Simplified apply logic (replicates _apply_move from Python engine.py)
        if mv.is_drop {
            if let Some(drop_piece_type) = mv.drop_piece {
                *new_board
                    .hand
                    .get_mut(&new_board.turn)
                    .unwrap()
                    .get_mut(&drop_piece_type)
                    .unwrap() -= 1;
                new_board.put_piece(
                    mv.to_sq % 9,
                    mv.to_sq / 9,
                    PieceType::make_piece(drop_piece_type, new_board.turn),
                );
            }
        } else {
            // Move on board
            let from_sq_idx = mv.from_sq.unwrap() as usize;
            let src_piece_val = new_board.squares[from_sq_idx];
            let mut p_type = PieceType::type_of(src_piece_val);

            // Capture?
            let dst_piece_val = new_board.squares[mv.to_sq as usize];
            if dst_piece_val != (PieceType::Empty as u8) {
                let captured_type = PieceType::type_of(dst_piece_val);
                // Demote if promoted
                let demoted_type = captured_type.demote();
                *new_board
                    .hand
                    .get_mut(&new_board.turn)
                    .unwrap()
                    .entry(demoted_type)
                    .or_insert(0) += 1;
            }

            // Promote?
            if mv.promote {
                p_type = p_type.promote();
            }

            // Update board
            new_board.squares[from_sq_idx] = PieceType::Empty as u8;
            new_board.squares[mv.to_sq as usize] = PieceType::make_piece(p_type, new_board.turn);
        }

        new_board.turn = new_board.turn.opposite();
        new_board.move_number += 1;
        new_board
    }
}
