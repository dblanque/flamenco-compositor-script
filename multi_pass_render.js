// SPDX-License-Identifier: GPL-3.0-or-later

// Author: Dylan Blanque
// Reviewer: Sybren Stüvel
// Updated: 2023-03-24
// License: Script is licensed under GNUGPLv3
// Blender Job for Flamenco Network Rendering with Compositor Support and
// Multi-platform compatibility.

const JOB_TYPE = {
    label: "Multi-Pass Render (Blender Cycles)",
    settings: [
        // Settings for artists to determine:
        { key: "frames", type: "string", required: true, eval: "f'{C.scene.frame_start}-{C.scene.frame_end}'",
          description: "Frame range to render. Examples: '47', '1-30', '3, 5-10, 47-327'" },
        { key: "chunk_size", type: "int32", default: 1, description: "Number of frames to render in one Blender render task",
          visible: "submission" },

        // render_output_root + add_path_components determine the value of render_output_path.
        { key: "render_output_root", type: "string", subtype: "dir_path", required: true, visible: "submission",
          description: "Base directory of where render output is stored. Will have some job-specific parts appended to it"},
        { key: "add_path_components", type: "int32", required: true, default: 0, propargs: {min: 0, max: 32}, visible: "submission",
          description: "Number of path components of the current blend file to use in the render output path"},
        { key: "render_output_path", type: "string", subtype: "file_path", editable: false,
          eval: "str(Path(abspath(settings.render_output_root), last_n_dir_parts(settings.add_path_components), jobname, '{timestamp}', '######'))",
          description: "Final file path of where render output will be saved"},

        // Automatically evaluated settings:
        { key: "blendfile", type: "string", required: true, description: "Path of the Blend file to render", visible: "web" },
        { key: "jobname", type: "string", required: true, eval: "str(jobname)", description: "Name of the Job", visible: "hidden" },
        { key: "filename", type: "string", required: true, eval: "bpy.path.basename(bpy.context.blend_data.filepath)", description: "Name of the Blend file to render", visible: "web" },
        { key: "fps", type: "float", eval: "C.scene.render.fps / C.scene.render.fps_base", visible: "hidden" },
        { key: "format", type: "string", required: true, eval: "C.scene.render.image_settings.file_format", visible: "web" },
        { key: "image_file_extension", type: "string", required: true, eval: "C.scene.render.file_extension", visible: "hidden",
          description: "File extension used when rendering images" },
        { key: "has_previews", type: "bool", required: false, eval: "C.scene.render.image_settings.use_preview", visible: "hidden",
          description: "Whether Blender will render preview images."},
    ]
};


// Set of scene.render.image_settings.file_format values that produce
// files which FFmpeg is known not to handle as input.
const ffmpegIncompatibleImageFormats = new Set([
    "EXR",
    "MULTILAYER", // Old CLI-style format indicators
    "OPEN_EXR",
    "OPEN_EXR_MULTILAYER", // DNA values for these formats.
]);

// File formats that would cause rendering to video.
// This is not supported by this job type.
const videoFormats = ['FFMPEG', 'AVI_RAW', 'AVI_JPEG'];

function compileJob(job) {
    print("Blender Render job submitted");
    print("job: ", job);

    const settings = job.settings;
    if (videoFormats.indexOf(settings.format) >= 0) {
        throw `This job type only renders images, and not "${settings.format}"`;
    }

    const renderOutput = renderOutputPath(job);

    // Make sure that when the job is investigated later, it shows the
    // actually-used render output:
    settings.render_output_path = renderOutput;

    const renderDir = path.dirname(renderOutput);
    const renderTasks = authorRenderTasks(settings, renderDir, renderOutput);

    for (const rt of renderTasks) {
        job.addTask(rt);
    }
}

// Do field replacement on the render output path.
function renderOutputPath(job) {
    let path = job.settings.render_output_path;
    if (!path) {
        throw "no render_output_path setting!";
    }
    return path.replace(/{([^}]+)}/g, (match, group0) => {
        switch (group0) {
        case "timestamp":
            return formatTimestampLocal(job.created);
        default:
            return match;
        }
    });
}

function authorRenderTasks(settings, renderDir, renderOutput) {
    print("authorRenderTasks(", renderDir, renderOutput, ")");
    let renderTasks = [];
    let chunks = frameChunker(settings.frames, settings.chunk_size);
    const blendfile_name = settings.blendfile.replace(/^.*[\\\/]/, '')

    if (settings.format == "TARGA") {
        settings.format = "TGA"
    }

    // Ensures the correct path if the job is duplicated
    const new_job_name_array = settings.blendfile.replace("\\", "/").split("/")
    const new_job_name = new_job_name_array[new_job_name_array.length - 2]

    for (let chunk of chunks) {
        const task = author.Task(`render-${chunk}`, "blender");
        const command = author.Command("blender-render", {
            exe: "{blender}",
            exeArgs: "{blenderArgs}",
            argsBefore: [
                "-P", path.join("{clientStoragePath}", "{jobSubPath}", "startup_script.py"),
            ],
            blendfile: path.join("{clientStoragePath}", "{jobSubPath}", new_job_name, blendfile_name),
            args: [
                "-noaudio",
                "--render-output", path.join("{clientStoragePath}", "{renderSubPath}", new_job_name, path.basename(renderOutput)),
                // ▼ Original Render Output Argument ▼
                // "--render-output", path.join(renderDir, path.basename(renderOutput)),
                "--render-format", settings.format,
                "--render-frame", chunk.replace("-", ".."), // Convert to Blender frame range notation.
                "--python-expr", "import bpy; bcs = bpy.context.scene; bcs.render.use_compositing = True; bcs.use_nodes = True",
                "--", // ◄ Blender ignores every argument after this line
                "--custom-script",
                "--device-type", "{deviceType}",
            ],
        });
        task.addCommand(command);
        renderTasks.push(task);
    }
    return renderTasks;
}
