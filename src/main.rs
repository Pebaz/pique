use std::env;
use std::io::{self, Read};
use json;

fn main() {
    let stdin = io::stdin();
    let mut handle = stdin.lock();
    let mut buffer = String::new();

    if let Ok(_) = handle.read_to_string(&mut buffer) {
        if let Ok(object) = json::parse(&mut buffer) {
            let mut result = &object;

            for arg in env::args().skip(1) {
                result = &result[&arg];
            }
    
            println!("{:#}", result);
        }

        else {
            println!("Error parsing JSON input");
        }
    }
}
