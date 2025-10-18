# 📱 Registration Error Handling - Quick Implementation Guide

> Quick reference for handling errors in OTP-based registration flow

---

## 🔄 Registration Flow

```
1. Send OTP → 2. Verify OTP → 3. Register User
```

---

## 📋 Error Handling by Endpoint

### 1. **POST /api/v1/auth/send-otp**

**Request:**
```json
{
  "mobile_number": "9876543210"
}
```

**Possible Errors:**

| Status Code | Error | Reason | User Message |
|-------------|-------|--------|--------------|
| 400 | Invalid mobile number | Not 10 digits or invalid format | "Please enter a valid 10-digit mobile number" |
| 409 | Mobile already registered | User exists in database | "This mobile number is already registered. Please login." |
| 429 | Too many requests | Rate limit exceeded | "Too many attempts. Please try again in 5 minutes." |
| 500 | Failed to send OTP | SMS service error | "Failed to send OTP. Please try again." |

**Success Response (200):**
```json
{
  "message": "OTP sent successfully",
  "mobile_number": "9876543210"
}
```

**React Native Implementation:**
```javascript
const sendOTP = async (mobileNumber) => {
  try {
    const response = await fetch('http://192.168.1.3:8000/api/v1/auth/send-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile_number: mobileNumber })
    });

    const data = await response.json();

    if (!response.ok) {
      // Handle specific error codes
      switch (response.status) {
        case 400:
          throw new Error('Please enter a valid 10-digit mobile number');
        case 409:
          throw new Error('This mobile number is already registered. Please login.');
        case 429:
          throw new Error('Too many attempts. Please try again in 5 minutes.');
        case 500:
          throw new Error('Failed to send OTP. Please try again.');
        default:
          throw new Error(data.detail || 'Something went wrong');
      }
    }

    return data;
  } catch (error) {
    throw error;
  }
};
```

---

### 2. **POST /api/v1/auth/verify-otp**

**Request:**
```json
{
  "mobile_number": "9876543210",
  "otp": "123456"
}
```

**Possible Errors:**

| Status Code | Error | Reason | User Message |
|-------------|-------|--------|--------------|
| 400 | Invalid OTP | OTP not 6 digits | "Please enter a valid 6-digit OTP" |
| 401 | OTP verification failed | Wrong OTP or expired | "Invalid or expired OTP. Please try again." |
| 404 | Mobile not found | No OTP sent for this number | "Please request OTP first" |
| 500 | Server error | Database or service error | "Verification failed. Please try again." |

**Success Response (200):**
```json
{
  "message": "OTP verified successfully",
  "mobile_number": "9876543210",
  "verified": true
}
```

**React Native Implementation:**
```javascript
const verifyOTP = async (mobileNumber, otp) => {
  try {
    const response = await fetch('http://192.168.1.3:8000/api/v1/auth/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mobile_number: mobileNumber,
        otp: otp
      })
    });

    const data = await response.json();

    if (!response.ok) {
      switch (response.status) {
        case 400:
          throw new Error('Please enter a valid 6-digit OTP');
        case 401:
          throw new Error('Invalid or expired OTP. Please try again.');
        case 404:
          throw new Error('Please request OTP first');
        case 500:
          throw new Error('Verification failed. Please try again.');
        default:
          throw new Error(data.detail || 'Something went wrong');
      }
    }

    return data;
  } catch (error) {
    throw error;
  }
};
```

---

### 3. **POST /api/v1/auth/register**

**Request:**
```json
{
  "mobile_number": "9876543210",
  "full_name": "John Doe",
  "otp": "123456"
}
```

**Possible Errors:**

| Status Code | Error | Reason | User Message |
|-------------|-------|--------|--------------|
| 400 | Validation error | Missing name or invalid format | "Please provide your full name" |
| 401 | OTP not verified | OTP verification pending | "Please verify OTP first" |
| 409 | Already registered | User exists | "Mobile number already registered" |
| 500 | Registration failed | Database error | "Registration failed. Please try again." |

**Success Response (201):**
```json
{
  "message": "Registration successful",
  "user": {
    "id": "uuid",
    "mobile_number": "9876543210",
    "full_name": "John Doe"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**React Native Implementation:**
```javascript
const register = async (mobileNumber, fullName, otp) => {
  try {
    const response = await fetch('http://192.168.1.3:8000/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mobile_number: mobileNumber,
        full_name: fullName,
        otp: otp
      })
    });

    const data = await response.json();

    if (!response.ok) {
      switch (response.status) {
        case 400:
          throw new Error('Please provide your full name');
        case 401:
          throw new Error('Please verify OTP first');
        case 409:
          throw new Error('Mobile number already registered');
        case 500:
          throw new Error('Registration failed. Please try again.');
        default:
          throw new Error(data.detail || 'Something went wrong');
      }
    }

    // Save tokens
    await AsyncStorage.setItem('auth_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);

    return data;
  } catch (error) {
    throw error;
  }
};
```

---

## 🎯 Complete Registration Flow with Error Handling

```javascript
import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { TextInput, Button, Text, Snackbar } from 'react-native-paper';

export const RegistrationScreen = () => {
  const [mobile, setMobile] = useState('');
  const [otp, setOTP] = useState('');
  const [name, setName] = useState('');
  const [step, setStep] = useState(1); // 1: mobile, 2: OTP, 3: name
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSendOTP = async () => {
    try {
      setLoading(true);
      setError('');

      await sendOTP(mobile);

      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOTP = async () => {
    try {
      setLoading(true);
      setError('');

      await verifyOTP(mobile, otp);

      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    try {
      setLoading(true);
      setError('');

      const result = await register(mobile, name, otp);

      // Navigate to home screen
      console.log('Registration successful:', result);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Step 1: Mobile Number */}
      {step === 1 && (
        <>
          <Text variant="headlineMedium">Enter Mobile Number</Text>
          <TextInput
            mode="outlined"
            label="Mobile Number"
            keyboardType="phone-pad"
            maxLength={10}
            value={mobile}
            onChangeText={setMobile}
            disabled={loading}
          />
          <Button
            mode="contained"
            onPress={handleSendOTP}
            loading={loading}
            disabled={mobile.length !== 10}
          >
            Send OTP
          </Button>
        </>
      )}

      {/* Step 2: OTP Verification */}
      {step === 2 && (
        <>
          <Text variant="headlineMedium">Enter OTP</Text>
          <Text variant="bodyMedium">
            OTP sent to {mobile}
          </Text>
          <TextInput
            mode="outlined"
            label="OTP"
            keyboardType="number-pad"
            maxLength={6}
            value={otp}
            onChangeText={setOTP}
            disabled={loading}
          />
          <Button
            mode="contained"
            onPress={handleVerifyOTP}
            loading={loading}
            disabled={otp.length !== 6}
          >
            Verify OTP
          </Button>
          <Button
            mode="text"
            onPress={handleSendOTP}
            disabled={loading}
          >
            Resend OTP
          </Button>
        </>
      )}

      {/* Step 3: Name */}
      {step === 3 && (
        <>
          <Text variant="headlineMedium">Complete Registration</Text>
          <TextInput
            mode="outlined"
            label="Full Name"
            value={name}
            onChangeText={setName}
            disabled={loading}
          />
          <Button
            mode="contained"
            onPress={handleRegister}
            loading={loading}
            disabled={!name.trim()}
          >
            Register
          </Button>
        </>
      )}

      {/* Error Snackbar */}
      <Snackbar
        visible={!!error}
        onDismiss={() => setError('')}
        duration={4000}
        action={{
          label: 'Dismiss',
          onPress: () => setError(''),
        }}
      >
        {error}
      </Snackbar>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    justifyContent: 'center',
    gap: 16,
  },
});
```

---

## ⚡ Quick Checklist

### Frontend (React Native)
- ✅ Validate mobile number (10 digits) before sending OTP
- ✅ Validate OTP (6 digits) before verification
- ✅ Show loading state during API calls
- ✅ Display user-friendly error messages
- ✅ Allow OTP resend with cooldown (60 seconds)
- ✅ Save tokens to AsyncStorage after registration
- ✅ Clear sensitive data (OTP) after use

### Backend Error Codes
- ✅ 400 - Validation errors
- ✅ 401 - Authentication/verification failed
- ✅ 404 - Resource not found
- ✅ 409 - Conflict (already exists)
- ✅ 429 - Rate limit exceeded
- ✅ 500 - Server error

### User Experience
- ✅ Clear error messages (no technical jargon)
- ✅ Show which step user is on (1/3, 2/3, 3/3)
- ✅ Allow going back to previous steps
- ✅ Disable buttons during loading
- ✅ Auto-dismiss success messages
- ✅ Keep error messages visible until dismissed

---

## 🔒 Security Notes

1. **Never log OTP** in production
2. **Clear OTP** from state after verification
3. **Implement rate limiting** on frontend (prevent spam)
4. **Store tokens securely** using AsyncStorage or Keychain
5. **Validate on both** frontend and backend

---

**Last Updated:** October 17, 2025
