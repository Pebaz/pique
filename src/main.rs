#[macro_use] extern crate rustpython_vm as rvm;
use std::env;
use std::io::{self, Read};
use json;
//use rustpython_compiler as compiler;
//use rustpython_vm as vm;


fn parse_commands() -> Vec<String> {
    vec![]
}


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

    // https://github.com/pickitup247/pyckitup/blob/master/src/main.rs
    let mut vm = rvm::VirtualMachine::new();

    let code_obj = rvm::compile::compile(
        "print([i for i in range(10)])\n",
        &rvm::compile::Mode::Exec,
        "<embedded>".to_owned(),
        vm.ctx.code_type()
    ).unwrap();
    
    let builtin = vm.get_builtin_scope();
    let scope = vm.context().new_scope(Some(builtin));
    let result = vm.run_code_obj(code_obj, scope.clone());
    match result {
        Ok(res) => {
            println!("{}", res);
        }

        Err(py_err) => {
            println!("{}", vm.to_pystr(&py_err).unwrap());
        }
    }
}
