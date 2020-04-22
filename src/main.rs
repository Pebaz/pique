// https://fasterthanli.me/blog/2020/a-half-hour-to-learn-rust/

fn for_each_planet<function_type>(f: function_type)
    where function_type: Fn(&'static str)
{
    f("Earth");
    f("Mars");
    f("Jupiter");
}

fn main() {
    for_each_planet(|planet| println!("Hello {}", planet));
}
