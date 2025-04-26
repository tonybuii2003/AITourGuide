import React, { useState, useRef } from 'react';
import { View, Button, Text, Alert, Dimensions, TouchableOpacity, StyleSheet } from 'react-native';
import { Audio, AVPlaybackSource } from 'expo-av';
import axios from 'axios';

const { width } = Dimensions.get('window');
// Define custom recording options for iOS, Android, and web.
const recordingOptions: Audio.RecordingOptions = {
  android: {
    extension: '.m4a',
    outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_MPEG_4,
    audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_AAC,
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 128000,
  },
  ios: {
    extension: '.m4a',
    audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
    sampleRate: 16000,
    numberOfChannels: 1,
    bitRate: 128000,
    linearPCMBitDepth: 16,
    linearPCMIsBigEndian: false,
    linearPCMIsFloat: false,
  },
  web: {
    mimeType: 'audio/webm',
  },
};

const VoiceRecorder: React.FC = () => {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [recordedUri, setRecordedUri] = useState<string | null>(null);
  const [amplitude, setAmplitude] = useState<number>(0);
  const amplitudeInterval = useRef<NodeJS.Timeout | null>(null);
  const startRecording = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission required', 'Please grant audio recording permission.');
        return;
      }

      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      // Create and start a new recording using the custom options.
      const newRecording = new Audio.Recording();
      await newRecording.prepareToRecordAsync(recordingOptions);
      await newRecording.startAsync();
      setRecording(newRecording);
      console.log('Recording started');

      amplitudeInterval.current = setInterval(() => {
        setAmplitude(Math.random()); // Simulated amplitude value between 0 and 1
      }, 100);
    } catch (error: any) {
      Alert.alert('Error', 'Failed to start recording: ' + error.message);
    }
  };

  const stopRecording = async () => {
    if (!recording) return;
    try {
        if (amplitudeInterval.current) {
            clearInterval(amplitudeInterval.current);
            amplitudeInterval.current = null;
          }
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecordedUri(uri);
      setRecording(null);
      console.log('Recording saved at:', uri);
      if (uri) {
        await uploadRecording(uri);
      }
    } catch (error: any) {
      Alert.alert('Error', 'Failed to stop recording: ' + error.message);
    }
  };

  const uploadRecording = async (uri: string) => {
    // Create a FormData instance and append the audio file.
    const formData = new FormData();
    formData.append('audio', {
      uri: uri,
      name: 'recording.m4a', // Change this if you convert to WAV on the backend.
      type: 'audio/x-m4a',    // Adjust MIME type as needed.
    } as any); // "as any" bypasses some TS restrictions on file types.

    try {
      const response = await axios.post('http://your-backend-url/api/upload-audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Server response:', response.data);
      Alert.alert('Upload Success', JSON.stringify(response.data));
    } catch (error: any) {
      console.error('Upload error:', error);
      Alert.alert('Upload Error', error.message);
    }
  };
  const AudioVisualizer = () => {
    const barWidth = width * amplitude; // full width when amplitude = 1
    return (
      <View style={styles.visualizerContainer}>
        <View style={[styles.visualizerBar, { width: barWidth }]} />
      </View>
    );
  };
  return (
    <View style={styles.container}>
      {/* Display the visualizer at the top */}
      <AudioVisualizer />

      {/* Record button at the bottom */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.recordButton}
          onPressIn={startRecording}
          onPressOut={stopRecording}
        >
          <Text style={styles.buttonText}>
            {recording ? 'Recording...' : 'Hold to Record'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}
const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: '#fff',
      justifyContent: 'center',
    },
    visualizerContainer: {
      position: 'absolute',
      top: 50,
      left: '5%',
      width: '90%',
      height: 20,
      backgroundColor: '#eee',
      borderRadius: 10,
      overflow: 'hidden',
    },
    visualizerBar: {
      height: '100%',
      backgroundColor: '#4CAF50',
    },
    buttonContainer: {
      position: 'absolute',
      bottom: 50,
      width: '100%',
      alignItems: 'center',
    },
    recordButton: {
      backgroundColor: '#f44336',
      paddingVertical: 15,
      paddingHorizontal: 30,
      borderRadius: 30,
    },
    buttonText: {
      color: '#fff',
      fontSize: 18,
    },
  });
export default VoiceRecorder;
