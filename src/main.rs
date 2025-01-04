use image::{Rgba, RgbaImage};
use imageproc::{filter::gaussian_blur_f32, map::map_colors};
use rand::Rng;
use std::env;
use std::path::Path;

const NOISE_RANGE: std::ops::Range<f32> = -24.2..24.2;
const VIGNETTE_STRENGTH: f32 = 0.77;

// Apply cyan filter and reduce image to greyscale
fn apply_color_filter(image: &mut RgbaImage) {
    println!("Adding color filter...");
    *image = map_colors(image, |p| {
        // Reduce red channel
        let r = p[0].saturating_sub(90);
        
        // Average RGB to create greyscale value
        let grey = ((r as u32 + p[1] as u32 + p[2] as u32) / 3) as u8;
        
        Rgba([grey, grey, grey, p[3]])
    });
}

// Add random film grain noise to the image and apply a slight blur
fn add_film_grain(image: &mut RgbaImage) {
    let mut rng = rand::thread_rng();

    // Iterate through each pixel in the image and apply noise
    for (_x, _y, pixel) in image.enumerate_pixels_mut() {
        let (r, g, b, a) = (pixel[0] as f32, pixel[1] as f32, pixel[2] as f32, pixel[3]);

        // Adjust the noise applied to each color channel
        let noise_r = adjust_noise(r, rng.gen_range(NOISE_RANGE.clone()));
        let noise_g = adjust_noise(g, rng.gen_range(NOISE_RANGE.clone()));
        let noise_b = adjust_noise(b, rng.gen_range(NOISE_RANGE.clone()));

        // Clamp the noisy pixel values to the valid RGB range
        pixel[0] = (r + noise_r).clamp(0.0, 255.0) as u8;
        pixel[1] = (g + noise_g).clamp(0.0, 255.0) as u8;
        pixel[2] = (b + noise_b).clamp(0.0, 255.0) as u8;
        pixel[3] = a;
    }

    // Apply a slight Gaussian blur to the image
    *image = gaussian_blur_f32(image, 0.5);
}

// Adjust the noise applied to a color channel by reducing it for extreme values
fn adjust_noise(channel: f32, noise: f32) -> f32 {
    if channel == 0.0 || channel == 255.0 {
        noise * 0.5
    } else {
        noise
    }
}

// Apply a vignette effect to the image by darkening the corners
fn apply_vignette(image: &mut RgbaImage) {
    let (width, height) = image.dimensions();
    let (center_x, center_y) = (width as f32 / 2.0, height as f32 / 2.0); // Image center coordinates

    // Iterate through each pixel and apply vignette effect based on distance from the center
    for (_x, _y, pixel) in image.enumerate_pixels_mut() {
        let (r, g, b, a) = (pixel[0] as f32, pixel[1] as f32, pixel[2] as f32, pixel[3]);
        let distance = ((_x as f32 - center_x).powi(2) + (_y as f32 - center_y).powi(2)).sqrt(); // Distance from center
        let max_distance = (center_x.powi(2) + center_y.powi(2)).sqrt(); // Max possible distance from the center
        let vignette_factor =
            (1.0 - ((distance / max_distance).powi(2) * VIGNETTE_STRENGTH)).clamp(0.0, 1.0); // Vignette strength

        // Apply the vignette factor to each color channel
        pixel[0] = (r * vignette_factor).clamp(0.0, 255.0) as u8;
        pixel[1] = (g * vignette_factor).clamp(0.0, 255.0) as u8;
        pixel[2] = (b * vignette_factor).clamp(0.0, 255.0) as u8;
        pixel[3] = a;
    }
}

fn main() {
    // Read the input image path from command line arguments
    let input_filename = env::args()
        .nth(1)
        .expect("Please provide an input image path");
    let path = Path::new(&input_filename);

    // Open the image from the given path
    let img = match image::open(path) {
        Ok(img) => img,
        Err(_) => panic!("Could not load image at {:?}", path),
    };
    let mut rgba_img = img.to_rgba8();

    // Apply the various image filters
    add_film_grain(&mut rgba_img);
    apply_color_filter(&mut rgba_img);
    apply_vignette(&mut rgba_img);

    // Save the modified image with a new filename
    let file_stem = path.file_stem().unwrap().to_str().unwrap();
    rgba_img
        .save(path.with_file_name(format!("{}_ortho.png", file_stem)))
        .unwrap();

    println!("Image processed successfully.")
}
