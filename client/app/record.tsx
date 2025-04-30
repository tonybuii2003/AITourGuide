// app/voice.tsx
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  StyleSheet,
  TouchableOpacity,
  Platform,
  Animated,
  Easing,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Audio } from 'expo-av';
import { useRouter } from 'expo-router';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import { Buffer } from 'buffer';

export default function VoiceChatScreen() {
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [guestId, setGuestId]     = useState<string | null>(null);
  const [level, setLevel]         = useState(0);           // 0–1 RMS
  const pulse = useRef(new Animated.Value(1)).current;
  const meterInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const silenceTicks  = useRef(0);
  const router        = useRouter();
  const [loading, setLoading] = useState(false);

  const METER_INTERVAL_MS   = 100;
  const SILENCE_THRESHOLD   = 0.03;
  const SILENCE_DURATION_MS = 5000;

  // Load or generate guestId
  useEffect(() => {
    (async () => {
      let id = await AsyncStorage.getItem('guestId');
      if (!id) {
        id = uuidv4();
        await AsyncStorage.setItem('guestId', id);
      }
      setGuestId(id);
    })();
  }, []);

  // Animate circle on level change
  useEffect(() => {
    const target = 1 + level * 0.3;
    Animated.spring(pulse, {
      toValue: target,
      useNativeDriver: true,
      stiffness: 200,
      damping: 20,
    }).start();
  }, [level]);

  // Start recording + live metering
  const startRecording = async () => {
    
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        return Alert.alert('Permission needed', 'Please grant audio permission');
      }
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      if (recording) {
        try {
          await recording.stopAndUnloadAsync();
        } catch { /* ignore */ }
        setRecording(null);
      }
      const rec = new Audio.Recording();
      await rec.prepareToRecordAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY);
      await rec.startAsync();
      setRecording(rec);
      silenceTicks.current = 0;

      // poll for dB → level
      meterInterval.current = setInterval(async () => {
        const stat = await rec.getStatusAsync();
        if (!stat.isRecording) return;
        const amp = Math.min(
          1,
          Math.max(0, ((stat.metering ?? -160) + 160) / 160)
        );
        setLevel(amp);

        // auto‐stop on silence
        if (amp < SILENCE_THRESHOLD) {
          silenceTicks.current += 1;
          if (silenceTicks.current * METER_INTERVAL_MS >= SILENCE_DURATION_MS) {
            clearInterval(meterInterval.current!);
            meterInterval.current = null;
            stopRecording();
          }
        } else {
          silenceTicks.current = 0;
        }
      }, METER_INTERVAL_MS);
    } catch (err: any) {
      console.error(err);
      Alert.alert('Error', 'Could not start recording: ' + err.message);
    }
  };

  // Stop recording, teardown, upload & play
  const stopRecording = async () => {
    try {
      const rec = recording;
      if (!rec) return;
      setRecording(null);

      if (meterInterval.current) {
        clearInterval(meterInterval.current);
        meterInterval.current = null;
      }

      await rec.stopAndUnloadAsync();
      setLevel(0);
      silenceTicks.current = 0;

      const uri = rec.getURI();
      console.log('Stopped ➞', uri);
      if (uri) await uploadAndPlay(uri);
    } catch (err: any) {
      console.error(err);
      Alert.alert('Error', 'Could not stop recording: ' + err.message);
    }
  };

  // Upload + playback
  const uploadAndPlay = async (blobUri: string) => {
    if (!guestId) {
      return Alert.alert('Error', 'No guestId');
    }
    setLoading(true);
    try {
      let data: Blob | string;
      if (Platform.OS === 'web') {
        const resp = await fetch(blobUri);
        data = await resp.blob();
      } else {
        data = await FileSystem.readAsStringAsync(blobUri, {
          encoding: FileSystem.EncodingType.Base64,
        });
      }

      const form = new FormData();
      if (Platform.OS === 'web') {
        form.append('audio', data as Blob, 'recording.webm');
      } else {
        const bin = Buffer.from(data as string, 'base64');
        form.append('audio', new Blob([bin]), 'recording.webm');
      }

      const axiosResp = await axios.post(
        `http://localhost:8083/api/guests/${guestId}/audio`,
        form,
        { responseType: 'arraybuffer' }
      );
      const audioBytes = axiosResp.data as ArrayBuffer;

      if (Platform.OS === 'web') {
        const url = URL.createObjectURL(
          new Blob([audioBytes], { type: 'audio/wav' })
        );
        const player = new window.Audio(url);
        player.play().catch(err => console.error('Audio.play() failed', err));
      } else {
        const fileUri = FileSystem.cacheDirectory + 'reply.wav';
        await FileSystem.writeAsStringAsync(
          fileUri,
          Buffer.from(audioBytes).toString('base64'),
          { encoding: FileSystem.EncodingType.Base64 }
        );
        const { sound } = await Audio.Sound.createAsync({ uri: fileUri });
        await sound.playAsync();
      }
    } catch (err: any) {
      console.error('upload/play error', err);
      Alert.alert('Upload/Play Error', err.message || err.toString());
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* mouth visualizer */}
      <View style={styles.mouthContainer}>
        <View style={[styles.mouthTop,    { height: 10 + level * 50 }]} />
        <View style={[styles.mouthBottom, { height: 10 + level * 50 }]} />
      </View>

      <Animated.View style={{ transform: [{ scale: pulse }] }}>
        <TouchableOpacity
          style={[
            styles.recordButton,
            { backgroundColor: recording ? '#FFB703' : '#888' },
          ]}
          onPressIn={startRecording}
          onPressOut={stopRecording}
          disabled={loading}
        />
        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#FFF" />
          </View>
        )}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F7F5F2',
    alignItems: 'center',
    justifyContent: 'center',
  },
  mouthContainer: {
    alignItems: 'center',
    marginBottom: 50,
  },
  mouthTop: {
    width: 120,
    backgroundColor: '#444',
    borderTopLeftRadius: 60,
    borderTopRightRadius: 60,
  },
  mouthBottom: {
    width: 120,
    backgroundColor: '#444',
    borderBottomLeftRadius: 60,
    borderBottomRightRadius: 60,
    marginTop: -4,
  },
  recordButton: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#FFB703',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 5,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    borderRadius: 50,
    backgroundColor: 'rgba(0,0,0,0.5)', 
    alignItems: 'center',
    justifyContent: 'center',
  },
});
