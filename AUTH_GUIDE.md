# WealthWarriors Authentication Guide
**Simple Guide for React Native Developers**

## 📱 Authentication Types

1. **Mobile + Password** - Traditional login
2. **Mobile + OTP** - SMS verification (no password needed)

## 🔑 How Tokens Work

After successful login, you receive:
- **Access Token** (expires in 30 min) - Use for all API calls
- **Refresh Token** (expires in 7 days) - Get new access token

## 📋 Registration

```javascript
const register = async (mobile, password, fullName, email) => {
  const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mobile_number: mobile,     // 10 digits
      password: password,         // Min 8 chars, 1 upper, 1 lower, 1 digit, 1 special
      full_name: fullName,
      email: email || null        // Optional
    })
  });

  const data = await response.json();
  if (response.ok) {
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
  }
  return data;
};
```

## 🔐 Login with Password

```javascript
const loginPassword = async (mobile, password) => {
  const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mobile_number: mobile, password })
  });

  const data = await response.json();
  if (response.ok) {
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
  }
  return data;
};
```

## 📱 Login with OTP (2 Steps)

**Step 1: Send OTP**
```javascript
const sendOTP = async (mobile) => {
  await fetch('https://api.wealthwarriorshub.in/api/v1/auth/send-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mobile_number: mobile })
  });
  // User receives SMS with 6-digit OTP (valid for 5 minutes)
};
```

**Step 2: Login with OTP**
```javascript
const loginOTP = async (mobile, otp) => {
  const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/login-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mobile_number: mobile, otp })
  });

  const data = await response.json();
  if (response.ok) {
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
  }
  return data;
};
```

## 🚀 Making Authenticated API Calls

**Always include the access token in Authorization header:**

```javascript
const callAPI = async (endpoint, method = 'GET', body = null) => {
  const token = await AsyncStorage.getItem('access_token');

  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`  // ⭐ Required for protected routes
    },
    body: body ? JSON.stringify(body) : null
  };

  const response = await fetch(`https://api.wealthwarriorshub.in${endpoint}`, options);

  // Handle token expiry
  if (response.status === 401) {
    const refreshed = await refreshToken();
    if (refreshed) {
      return callAPI(endpoint, method, body); // Retry with new token
    } else {
      logout(); // Token refresh failed, logout user
      return null;
    }
  }

  return await response.json();
};
```

**Examples:**
```javascript
// Get user profile
const profile = await callAPI('/api/v1/users/me');

// Send chat message
const result = await callAPI('/api/v1/chat/message', 'POST', { message: 'Hello' });

// Get onboarding status
const status = await callAPI('/api/v1/onboarding/status');
```

## 🔄 Refresh Access Token

```javascript
const refreshToken = async () => {
  const refresh = await AsyncStorage.getItem('refresh_token');

  const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/refresh', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh })
  });

  const data = await response.json();
  if (response.ok) {
    await AsyncStorage.setItem('access_token', data.access_token);
    await AsyncStorage.setItem('refresh_token', data.refresh_token);
    return true;
  }
  return false;
};
```

## 🚪 Logout

```javascript
const logout = async () => {
  await AsyncStorage.removeItem('access_token');
  await AsyncStorage.removeItem('refresh_token');
  navigation.navigate('Login');
};
```

## ✅ Helper Functions

**Check Mobile Availability (for registration)**
```javascript
const checkMobile = async (mobile) => {
  const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/check-mobile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mobile_number: mobile })
  });
  const data = await response.json();
  return data.exists; // true = already registered, false = available
};
```

**Get Password Requirements**
```javascript
const getPasswordRules = async () => {
  const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/password-requirements');
  return await response.json();
  // Returns: { min_length: 8, requires_uppercase: true, ... }
};
```

## 🎯 Complete Login Screen Example

```javascript
import React, { useState } from 'react';
import { View, TextInput, Button, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function LoginScreen({ navigation }) {
  const [mobile, setMobile] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    const response = await fetch('https://api.wealthwarriorshub.in/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mobile_number: mobile, password })
    });

    const data = await response.json();

    if (response.ok) {
      await AsyncStorage.setItem('access_token', data.access_token);
      await AsyncStorage.setItem('refresh_token', data.refresh_token);
      navigation.navigate('Home');
    } else {
      Alert.alert('Login Failed', data.detail);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="Mobile Number"
        value={mobile}
        onChangeText={setMobile}
        keyboardType="phone-pad"
      />
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <Button title="Login" onPress={handleLogin} />
    </View>
  );
}
```

## 📝 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/auth/register` | POST | Register new user |
| `/api/v1/auth/login` | POST | Login with password |
| `/api/v1/auth/login-otp` | POST | Login with OTP |
| `/api/v1/auth/send-otp` | POST | Send OTP to mobile |
| `/api/v1/auth/refresh` | POST | Refresh access token |
| `/api/v1/auth/check-mobile` | POST | Check mobile exists |
| `/api/v1/auth/password-requirements` | GET | Get password rules |

## 🛡️ Security Tips

1. **Store tokens securely** - Use AsyncStorage, never in state
2. **Always use HTTPS** - All endpoints use secure connection
3. **Handle 401 errors** - Auto-refresh tokens when expired
4. **Clear tokens on logout** - Remove from storage completely
5. **Never log tokens** - Don't console.log tokens in production

---

**🎉 That's it! You're ready to implement secure authentication in your React Native app.**
