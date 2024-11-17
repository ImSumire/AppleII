#version 330

uniform sampler2D texture0;
uniform vec2 resolution;

in vec2 fragTexCoord;
in vec4 fragColor;

out vec4 finalColor;

void main() {
    // Invert y
    vec2 uv = vec2(fragTexCoord.x, 1.0 - fragTexCoord.y); // Already in [0, 1]

    vec4 color = texture(texture0, uv);

    // Scanlines
    float scanline = 0.9 + 0.1 * sin(uv.y * resolution.y * 2.0);
    color.rgb *= scanline;

    // Chromatic aberration
    vec2 offset = vec2(0.0015, 0.0);
    float r = texture(texture0, uv + offset).r;
    float g = color.g;
    float b = texture(texture0, uv - offset).b;
    color.rgb = vec3(r, g, b);

    // Vignette
    vec2 center = vec2(0.5, 0.5);
    float dist = distance(uv, center);
    color *= smoothstep(1.0, 0.4, dist);

    finalColor = color * fragColor;
}
