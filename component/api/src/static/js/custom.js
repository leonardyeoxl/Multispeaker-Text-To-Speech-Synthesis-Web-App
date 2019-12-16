// Mapping
var object_mapping = {
    0: [$("#upload-card"), $("#upload-name")],
    1: [$("#record-card"), $("#record-name")]
};

// Global
var g_selected_card = null;
var g_recording_state = false;

var g_constraints = { audio: true, video:false }
var g_upload_input_obj = $("#upload-input");
var g_audio_context_obj = null;
var g_mic_recorder_obj = null;
var g_recording_wav_obj = null;

var g_text_array = [];

// Class
var AudioContextCase = window.AudioContext || window.webkitAudioContext;

// Recording function
function ExportWav(blob) {
    var file_name = '{0}_{1}_recording.wav'.format(
        Date.today().toString('ddMMyyyy'),
        new Date().toString('HHmm')
    );
    g_recording_wav_obj = new File([blob], file_name);
}

function StartRecording(){
    //start recording
    g_mic_recorder_obj.clear();
    g_mic_recorder_obj.record();
}

function StopRecording(){
    //extract data
    g_mic_recorder_obj.stop();
    //extract blob
    g_mic_recorder_obj.exportWAV(ExportWav);
}

// Base64 function
function ConvertBase64ToBinary(base64) {
    var raw = window.atob(base64);
    var rawLength = raw.length;
    var array = new Uint8Array(new ArrayBuffer(rawLength));
  
    for(i = 0; i < rawLength; i++) {
      array[i] = raw.charCodeAt(i);
    }
    return array;
}

// Wavesurfer function
function ConstructWaveObj(id, height, cursorWidth = 1){
    return WaveSurfer.create({
        container: id,
        height: height,
        cursorWidth: cursorWidth,
        responsive: true,
        waveColor: '#D2EDD4',
        progressColor: '#46B54D',
        mediaControls: true
    });
}

// UI function
function UpdateCard(selected_id, text){
    if ( g_selected_card != null){
        object_mapping[g_selected_card][0].toggleClass("bg-success");
        object_mapping[g_selected_card][1].text(" ");
    }
    object_mapping[selected_id][0].toggleClass("bg-success");
    object_mapping[selected_id][1].text(text);
    g_selected_card = selected_id;
};

// function GetAudioFile(item_data){
//     return new File([ConvertBase64ToBinary(item_data)], "{0}.wav".format(item_data.slice(0,10), {type: "audio/wav"}));
// };

function GetAudioBlob(item_data){
    var audio_blob = new Blob([ConvertBase64ToBinary(item_data)], {type: "audio/wav"});
    return URL.createObjectURL(audio_blob);
};

// function GetResultRow(index, id){
//     // debug
//     console.log(g_text_array[index]); // Assumption "0" == 0
//     var audio_html = "<div id='{0}'></div>".format(id);
//     return "<tr><td>{0}</td><td>{1}</td></tr>".format(audio_html, g_text_array[index]);
// }

function ConvertBlobToDownloadURL(audio_blob_url){
    var download_created_date = "{0}{1}".format(new Date().toISOString(), '.wav')
    return "<a class='btn btn-primary' href='{0}' role='button' download='{1}'>Download {1}</a>".format(audio_blob_url, download_created_date);
}

function GetResultRow(index, audio_blob){
    // debug
    console.log(g_text_array[index]); // Assumption "0" == 0
    var audio_html = "<audio controls><source src='{0}' type='audio/wav'></audio>".format(audio_blob);
    var wav_url_download = ConvertBlobToDownloadURL(audio_blob);
    return "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(audio_html, g_text_array[index], wav_url_download);
}

// Event listeners
g_upload_input_obj.change(function(e){
    e.preventDefault();

    var filename = g_upload_input_obj.val().split('\\').pop();
    // update the g_recording_wav_obj
    g_recording_wav_obj = g_upload_input_obj.prop("files")[0];

    // Update UI
    UpdateCard(0, filename);
});

$("#upload-btn").click(function(e){
    e.preventDefault();

    g_upload_input_obj.trigger("click");
});

$("#record-btn").click(function(e){
    e.preventDefault();

    var text_to_display = "Recording...";

    if (g_recording_state != true){
        //create input stream
        navigator.mediaDevices.getUserMedia(g_constraints).then(function(stream) {
            //check if there is audio context
            if (g_audio_context_obj == null){
                g_audio_context_obj = new AudioContextCase(); //new audio context to help us record
            }
            //get audio stream
            input = g_audio_context_obj.createMediaStreamSource(stream);
            //create recorder instance
            g_mic_recorder_obj = new Recorder(input,{numChannels:1});
            //start recording
            StartRecording();
        }).catch(function(err){
            alert('Error getting audio');
            console.warn('Device error: ' + err);
        });
    }else{
        text_to_display = '{0}_{1}_recording.wav'.format(
            Date.today().toString('ddMMyyyy'),
            new Date().toString('HHmm')
        );
        StopRecording();
    }
    // toggle recording state
    g_recording_state = !g_recording_state;

    // Update UI
    UpdateCard(1, text_to_display);
});

$("#submit-btn").click(function(e){
    e.preventDefault();
    $("#table-body tr").remove();
    $("#loading-section").append("<div class='d-flex align-items-center'><strong>Processing audio and text...</strong><div class='spinner-border ml-auto' role='status' aria-hidden='true'></div></div>");
    call_tts("/api/tts");
});

// API calls function
function call_tts(url){
    var form_data = new FormData();

    // save text input into g_text_array
    var text_string = $("#text-input").val();
    g_text_array = text_string.split(".");
    // attach data
    form_data.append("files", g_recording_wav_obj);
    form_data.append("text", text_string);

    $.ajax({
        url: url,
        method: "POST",
        data: form_data,
        processData: false,
        contentType: false,
        enctype: "multipart/form-data",

        success: function(result){
            if (result["status"] === "ok"){
                // Drop all rows
                $("#table-body tr").remove();
                $("#loading-section div").remove();

                // // Add to result as table row
                // $.each(result["data"], function(index, item_data){
                //     var audio_blob = GetAudioFile(item_data);
                //     var audio_id = "audio_player_{0}".format(index);
                //     $("#table-body").append(GetResultRow(index, audio_id));
                //     var wave_surfer_obj = ConstructWaveObj("#{0}".format(audio_id), 100);
                //     //debug
                //     console.log(audio_blob);
                //     wave_surfer_obj.loadBlob(audio_blob);
                // });

                // Add to result as table row
                $.each(result["data"], function(index, item_data){
                    var audio_blob = GetAudioBlob(item_data);
                    $("#table-body").append(GetResultRow(index, audio_blob));
                });
            }else{
                alert(result["message"]);
            }
        },
        error: function(request, _status, _error){
            alert(request.responseText);
        }
    });
}