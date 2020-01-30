let conversationContext = '';
let recorder;
let context;


const recordMic = document.getElementById("stt2");
console.log(document.getElementById("stt2"));
recordMic.onclick = function() {
  const fullPath = recordMic.src;
  const filename = fullPath.replace(/^.*[\\/]/, '');
  console.log(filename);
  if (filename == 'microphone.jpg') {
    try {
      recordMic.src = 'static/mic_active.png';
      startRecording();
      console.log('recorder started');
      $('#search-q').val('I am listening ...');
    } catch (ex) {
      console.log("Recognizer error .....");
    }
  } else {
    stopRecording();
    $('#search-q').val('');
  }
};

function startUserMedia(stream) {
  const input = context.createMediaStreamSource(stream);
  console.log('Media stream created.');
  // Uncomment if you want the audio to feedback directly
  // input.connect(audio_context.destination);
  // console.log('Input connected to audio context destination.');

  // eslint-disable-next-line
  recorder = new Recorder(input);
  console.log('Recorder initialised.');
}

function startRecording(button) {
  recorder && recorder.record();
  console.log('Recording...');
}

function stopRecording(button) {
  recorder && recorder.stop();
  console.log('Stopped recording.');

  recorder &&
    recorder.exportWAV(function(blob) {
      console.log(blob);
      const url = '/';
      const request = new XMLHttpsRequest();
      request.open('POST', url, true);
      // request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

      // Decode asynchronously
      request.onload = function() {
        console.log(request.response);
      };
      request.send(blob);
    });

  recorder.clear();
}

window.onload = function init() {
  try {
    // webkit shim
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
    // eslint-disable-next-line
    window.URL = window.URL || window.webkitURL;

    context = new AudioContext();
    console.log('Audio context set up.');
    console.log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
  } catch (e) {
    alert('No web audio support in this browser!');
  }

  navigator.getUserMedia(
    {
      audio: true
    },
    startUserMedia,
    function(e) {
      console.log('No live audio input: ' + e);
    }
  );
};
