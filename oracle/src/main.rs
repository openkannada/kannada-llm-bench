// SPDX-FileCopyrightText: 2026 The Open Kannada Authors
// SPDX-License-Identifier: MIT OR Apache-2.0

//! Reads 1 text per line on stdin and writes 1 answer per line: the answer keys for the
//! transliteration and orthography items, computed with kannadi.
//!
//! oracle translit <from> <to>   transliterate between kannada, iso15919, iast and baraha
//! oracle modernize              Old Kannada letters to modern ones
//! oracle has-old                1 if the text has an Old Kannada letter, else 0

use std::io::{self, BufRead, BufWriter, Write};
use std::process::ExitCode;

use kannadi::{Scheme, has_old_kannada, modernize, transliterate};

fn answer_fn(args: &[String]) -> Result<Box<dyn Fn(&str) -> String>, String> {
    match args {
        [cmd, from, to] if cmd == "translit" => {
            let from: Scheme = from.parse().map_err(|e| format!("{e:?}"))?;
            let to: Scheme = to.parse().map_err(|e| format!("{e:?}"))?;
            Ok(Box::new(move |text| transliterate(text, from, to)))
        }
        [cmd] if cmd == "modernize" => Ok(Box::new(modernize)),
        [cmd] if cmd == "has-old" => {
            Ok(Box::new(|text| u8::from(has_old_kannada(text)).to_string()))
        }
        _ => Err("usage: oracle translit <from> <to> | modernize | has-old".into()),
    }
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let answer = match answer_fn(&args) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("{e}");
            return ExitCode::from(2);
        }
    };
    let mut out = BufWriter::new(io::stdout().lock());
    for line in io::stdin().lock().lines() {
        let Ok(line) = line else {
            return ExitCode::FAILURE;
        };
        if writeln!(out, "{}", answer(&line)).is_err() {
            return ExitCode::FAILURE;
        }
    }
    if out.flush().is_err() {
        return ExitCode::FAILURE;
    }
    ExitCode::SUCCESS
}

#[cfg(test)]
mod tests {
    use super::answer_fn;

    fn run(args: &[&str], text: &str) -> String {
        let args: Vec<String> = args.iter().map(ToString::to_string).collect();
        answer_fn(&args).unwrap()(text)
    }

    #[test]
    fn answers_each_command() {
        assert_eq!(run(&["translit", "kannada", "iso15919"], "ಕನ್ನಡ"), "kannaḍa");
        assert_eq!(run(&["translit", "iso15919", "kannada"], "kannaḍa"), "ಕನ್ನಡ");
        assert_eq!(run(&["modernize"], "ಅಱಿವು ಬಾೞ್"), "ಅರಿವು ಬಾಳ್");
        assert_eq!(run(&["has-old"], "ಬಾೞ್"), "1");
        assert_eq!(run(&["has-old"], "ಬಾಳು"), "0");
    }

    #[test]
    fn rejects_unknown_commands_and_schemes() {
        let args = |a: &[&str]| a.iter().map(ToString::to_string).collect::<Vec<_>>();
        assert!(answer_fn(&args(&["translit", "kannada", "klingon"])).is_err());
        assert!(answer_fn(&args(&["shout"])).is_err());
    }
}
