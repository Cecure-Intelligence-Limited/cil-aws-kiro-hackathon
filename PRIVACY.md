# Privacy Policy - Aura Desktop Assistant

## Overview

Aura Desktop Assistant is designed with privacy-first principles, implementing local-first processing with optional cloud services. This document outlines our privacy practices, data handling, and user controls.

## Privacy Principles

### 1. Local-First Architecture
- **Primary Processing**: All core functionality works offline using local models
- **Data Residency**: User data remains on local device by default, never leaves without explicit consent
- **Cloud Optional**: External services (Whisper, HuggingFace) are strictly opt-in with clear warnings
- **Transparency**: Real-time indicators show when cloud services are active
- **Offline Capability**: Full voice recognition, text processing, and file operations work without internet
- **Local Models**: Vosk for STT, local intent parsing, system TTS as defaults

### 2. Data Minimization
- **Collect Only Necessary**: Zero data collection beyond what's needed for immediate functionality
- **Retention Limits**: Automatic deletion of temporary data within seconds of processing
- **Purpose Limitation**: Data used only for explicitly stated purposes, never for analytics or profiling
- **Storage Minimization**: No persistent storage of voice data, minimal session storage
- **Processing Minimization**: Only process data when user explicitly requests it

### 3. User Control
- **Granular Consent**: Individual control over each cloud service with separate toggles
- **Easy Opt-out**: One-click disable for all cloud features with immediate effect
- **Data Export**: Complete export of all user data in standard formats
- **Data Deletion**: Cryptographic erasure and secure deletion on request
- **Audit Trail**: Complete log of all data processing activities available to user

## Data Categories and Handling

### Voice Data

#### Local Processing (Default)
- **Storage**: Temporary in-memory buffers only, cleared within 100ms of processing
- **Processing**: Local STT with Vosk (completely offline, no network required)
- **Retention**: Zero persistent storage - immediately deleted after transcription
- **Encryption**: Memory encryption during processing using OS secure memory APIs
- **Models**: Downloaded once, stored locally, never updated without user consent
- **Quality**: Supports 16+ languages with accuracy comparable to cloud services

#### Cloud Processing (Opt-in Only)
- **Service**: OpenAI Whisper API (requires explicit user consent)
- **Transmission**: TLS 1.3 encrypted HTTPS with certificate pinning
- **Retention**: Per OpenAI's data retention policy (30 days as of 2024)
- **Control**: Can be disabled instantly in settings with immediate effect
- **Indicators**: Clear visual/audio indicators when cloud processing is active
- **Fallback**: Automatically falls back to local processing if cloud is unavailable
- **Data Minimization**: Only audio data sent, no metadata or context

```typescript
// Voice data handling
class VoiceDataHandler {
  private audioBuffer: ArrayBuffer | null = null;
  
  async processVoice(audioData: ArrayBuffer, useCloud: boolean = false) {
    this.audioBuffer = audioData;
    
    try {
      if (useCloud && this.userConsent.cloudSTT) {
        // Cloud processing with user consent
        const transcript = await this.cloudSTT.transcribe(audioData);
        return transcript;
      } else {
        // Local processing (default)
        const transcript = await this.localSTT.transcribe(audioData);
        return transcript;
      }
    } finally {
      // Always clear audio data from memory
      this.clearAudioBuffer();
    }
  }
  
  private clearAudioBuffer() {
    if (this.audioBuffer) {
      // Secure memory clearing
      new Uint8Array(this.audioBuffer).fill(0);
      this.audioBuffer = null;
    }
  }
}
```

### Text Data

#### User Input
- **Storage**: Temporary session storage only
- **Processing**: Local intent parsing by default
- **Logging**: Redacted logs (see redaction heuristics below)
- **Retention**: Cleared on session end

#### File Content
- **Access**: Read-only access to user-specified files
- **Processing**: Local analysis preferred
- **Transmission**: Only to cloud services with explicit consent
- **Caching**: No persistent caching of file contents

### File System Access

#### Permissions Model
- **Safe Directories**: Restricted to user-designated folders
- **Read Permissions**: Only files explicitly opened by user
- **Write Permissions**: Only in safe directories
- **No System Files**: Cannot access system or application files

```python
# Least-privilege file access
class SecureFileAccess:
    def __init__(self):
        self.safe_directories = [
            Path.home() / "Documents" / "Aura",
            Path.home() / "Desktop",
            Path.cwd() / "data"
        ]
    
    def validate_access(self, requested_path: Path) -> bool:
        resolved_path = requested_path.resolve()
        
        # Check if path is within safe directories
        for safe_dir in self.safe_directories:
            try:
                resolved_path.relative_to(safe_dir)
                return True
            except ValueError:
                continue
        
        return False
```

## Cloud Service Integration

### Opt-in Consent Management

#### Granular Controls
- **Speech-to-Text**: Separate consent for Whisper API
- **Natural Language Processing**: Separate consent for GPT-4o
- **Text-to-Speech**: Separate consent for cloud TTS
- **Document AI**: Separate consent for Hugging Face APIs

#### Consent Interface
```typescript
interface PrivacyConsent {
  cloudSTT: boolean;           // Whisper API
  cloudNLP: boolean;           // GPT-4o intent parsing
  cloudTTS: boolean;           // Cloud text-to-speech
  documentAI: boolean;         // Hugging Face summarization
  analytics: boolean;          // Usage analytics
  crashReporting: boolean;     // Error reporting
}

// Consent management
class ConsentManager {
  async requestConsent(service: keyof PrivacyConsent): Promise<boolean> {
    const consent = await this.showConsentDialog({
      service,
      dataTypes: this.getDataTypes(service),
      retention: this.getRetentionPolicy(service),
      thirdParty: this.getThirdPartyInfo(service)
    });
    
    if (consent.granted) {
      this.logConsentEvent(service, consent);
    }
    
    return consent.granted;
  }
}
```

### Data Transmission Security

#### Encryption Standards
- **TLS Version**: TLS 1.3 minimum
- **Cipher Suites**: Only strong ciphers (AES-256-GCM)
- **Certificate Validation**: Full certificate chain validation
- **HSTS**: HTTP Strict Transport Security enabled

#### Request Security
```typescript
// Secure API request configuration
const secureRequest = {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${await getEncryptedApiKey()}`,
    'X-Request-ID': generateSecureUUID(),
    'X-Client-Version': APP_VERSION,
    'X-Timestamp': Date.now().toString()
  },
  body: JSON.stringify(redactedData),
  signal: AbortSignal.timeout(30000)
};
```

## Data Redaction Heuristics

### Automatic Redaction Patterns

Aura implements comprehensive data redaction to protect sensitive information in logs, cloud transmissions, and temporary storage.

#### Personal Identifiers
```typescript
const REDACTION_PATTERNS = {
  // Financial Information
  creditCard: /\b(?:\d{4}[-\s]?){3}\d{4}\b/g,
  bankAccount: /\b\d{8,17}\b/g,
  routingNumber: /\b\d{9}\b/g,
  
  // Government IDs
  ssn: /\b\d{3}-\d{2}-\d{4}\b/g,
  ein: /\b\d{2}-\d{7}\b/g,
  passport: /\b[A-Z]{1,2}\d{6,9}\b/g,
  
  // Contact Information
  email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
  phone: /\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b/g,
  
  // Network Information
  ipAddress: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
  macAddress: /\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b/g,
  
  // Credentials and Keys
  apiKey: /\b[A-Za-z0-9]{32,}\b/g,
  jwt: /\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g,
  password: /\b(password|passwd|pwd)\s*[:=]\s*\S+/gi,
  secret: /\b(secret|key|token|credential|auth)\s*[:=]\s*\S+/gi,
  
  // File System Paths
  userPath: /(?:C:\\Users\\[^\\]+|\/home\/[^\/]+|\/Users\/[^\/]+)/g,
  tempPath: /(?:C:\\temp\\|\/tmp\/|\/var\/tmp\/).*/g,
  
  // URLs with sensitive info
  urlWithAuth: /https?:\/\/[^:]+:[^@]+@[^\s]+/g,
  
  // Database connections
  dbConnection: /(?:mongodb|mysql|postgres|redis):\/\/[^\s]+/g,
};

class DataRedactor {
  private static instance: DataRedactor;
  private customPatterns: Map<string, RegExp> = new Map();
  
  static getInstance(): DataRedactor {
    if (!DataRedactor.instance) {
      DataRedactor.instance = new DataRedactor();
    }
    return DataRedactor.instance;
  }
  
  redactSensitiveData(text: string, preserveFormat: boolean = false): string {
    let redacted = text;
    
    Object.entries(REDACTION_PATTERNS).forEach(([type, pattern]) => {
      redacted = redacted.replace(pattern, (match) => {
        if (preserveFormat) {
          // Preserve format for readability
          return this.preserveFormatRedaction(match, type);
        }
        return `[REDACTED-${type.toUpperCase()}]`;
      });
    });
    
    // Apply custom patterns
    this.customPatterns.forEach((pattern, type) => {
      redacted = redacted.replace(pattern, `[REDACTED-${type.toUpperCase()}]`);
    });
    
    return redacted;
  }
  
  private preserveFormatRedaction(match: string, type: string): string {
    switch (type) {
      case 'creditCard':
        return match.replace(/\d/g, '*').replace(/\*{4}$/, match.slice(-4));
      case 'email':
        const [local, domain] = match.split('@');
        return `${local.charAt(0)}***@${domain}`;
      case 'phone':
        return match.replace(/\d/g, '*').replace(/\*{4}$/, match.slice(-4));
      default:
        return `[REDACTED-${type.toUpperCase()}]`;
    }
  }
  
  addCustomPattern(name: string, pattern: RegExp): void {
    this.customPatterns.set(name, pattern);
  }
}

function redactSensitiveData(text: string, preserveFormat: boolean = false): string {
  return DataRedactor.getInstance().redactSensitiveData(text, preserveFormat);
}
```

#### Context-Aware Redaction
```typescript
interface RedactionContext {
  domain: 'financial' | 'medical' | 'legal' | 'personal' | 'technical';
  sensitivity: 'low' | 'medium' | 'high' | 'critical';
  audience: 'internal' | 'external' | 'public';
}

class ContextAwareRedactor {
  private domainPatterns = {
    financial: {
      amounts: /\$[\d,]+\.?\d*/g,
      accounts: /\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b/g,
      institutions: /\b(bank|credit union|investment|brokerage)\s+\w+/gi,
      transactions: /\b(deposit|withdrawal|transfer|payment)\s+of\s+\$[\d,]+/gi
    },
    
    medical: {
      mrn: /\b(mrn|medical record)\s*[:=]?\s*\d+/gi,
      diagnosis: /\b(diagnosis|condition|disease)\s*[:=]?\s*[a-z\s]+/gi,
      medication: /\b(medication|drug|prescription)\s*[:=]?\s*[a-z\s]+/gi,
      provider: /\bdr\.?\s+[a-z]+/gi
    },
    
    legal: {
      caseNumbers: /\b(case|docket)\s*#?\s*\d+/gi,
      parties: /\b(plaintiff|defendant|petitioner|respondent)\s*[:=]?\s*[a-z\s]+/gi,
      attorneys: /\b(attorney|lawyer|counsel)\s*[:=]?\s*[a-z\s]+/gi
    },
    
    personal: {
      names: /\b[A-Z][a-z]+\s+[A-Z][a-z]+\b/g,
      addresses: /\b\d+\s+[A-Z][a-z\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct|place|pl)\b/gi,
      relationships: /\b(spouse|partner|child|parent|sibling)\s*[:=]?\s*[a-z\s]+/gi
    },
    
    technical: {
      servers: /\b(?:server|host|node)\s*[:=]?\s*[a-z0-9.-]+/gi,
      databases: /\b(?:database|db|schema)\s*[:=]?\s*[a-z0-9_]+/gi,
      environments: /\b(?:prod|production|staging|dev|development)\s*[:=]?\s*[a-z0-9.-]+/gi
    }
  };
  
  redactWithContext(text: string, context: RedactionContext): string {
    let redacted = redactSensitiveData(text);
    
    // Apply domain-specific patterns
    const patterns = this.domainPatterns[context.domain];
    if (patterns) {
      Object.entries(patterns).forEach(([type, pattern]) => {
        redacted = redacted.replace(pattern, `[REDACTED-${type.toUpperCase()}]`);
      });
    }
    
    // Apply sensitivity-based redaction
    if (context.sensitivity === 'critical') {
      // Redact all proper nouns
      redacted = redacted.replace(/\b[A-Z][a-z]+\b/g, '[REDACTED-NAME]');
    }
    
    // Apply audience-based redaction
    if (context.audience === 'external' || context.audience === 'public') {
      // More aggressive redaction for external sharing
      redacted = redacted.replace(/\b\d{2,}\b/g, '[REDACTED-NUMBER]');
      redacted = redacted.replace(/\b[A-Z]{2,}\b/g, '[REDACTED-CODE]');
    }
    
    return redacted;
  }
}

// Usage example
const redactor = new ContextAwareRedactor();
const sensitiveText = "Patient John Doe (MRN: 123456) was prescribed medication X for condition Y";
const context: RedactionContext = {
  domain: 'medical',
  sensitivity: 'high',
  audience: 'external'
};

const redactedText = redactor.redactWithContext(sensitiveText, context);
// Result: "Patient [REDACTED-NAME] ([REDACTED-MRN]) was prescribed [REDACTED-MEDICATION] for [REDACTED-DIAGNOSIS]"
```

#### Smart Redaction with Machine Learning
```typescript
class MLRedactor {
  private namedEntityRecognizer: any; // NLP model for entity recognition
  
  async intelligentRedaction(text: string): Promise<string> {
    // Use local NLP model to identify entities
    const entities = await this.namedEntityRecognizer.recognize(text);
    
    let redacted = text;
    
    entities.forEach(entity => {
      const { start, end, label, confidence } = entity;
      
      // Only redact high-confidence sensitive entities
      if (confidence > 0.8 && this.isSensitiveEntity(label)) {
        const entityText = text.substring(start, end);
        redacted = redacted.replace(entityText, `[REDACTED-${label}]`);
      }
    });
    
    return redacted;
  }
  
  private isSensitiveEntity(label: string): boolean {
    const sensitiveLabels = [
      'PERSON', 'ORG', 'GPE', 'MONEY', 'DATE', 
      'TIME', 'PERCENT', 'PHONE', 'EMAIL', 'SSN'
    ];
    return sensitiveLabels.includes(label);
  }
}
```

## User Rights and Controls

### Data Subject Rights

#### Right to Access
- **Data Export**: Complete export of all user data
- **Data Inventory**: List of all data categories stored
- **Processing Activities**: Log of all data processing activities

#### Right to Rectification
- **Data Correction**: Ability to correct inaccurate data
- **Settings Update**: Real-time settings changes
- **Consent Modification**: Change consent preferences anytime

#### Right to Erasure
- **Complete Deletion**: Remove all user data from local storage
- **Cloud Data Deletion**: Request deletion from cloud services
- **Secure Deletion**: Cryptographic erasure of encrypted data

#### Right to Portability
- **Data Export Formats**: JSON, CSV, plain text
- **Settings Export**: Complete configuration backup
- **Migration Tools**: Easy transfer to other systems

### Privacy Dashboard
```typescript
interface PrivacyDashboard {
  dataInventory: {
    voiceRecordings: number;
    textInputs: number;
    filesAccessed: number;
    settingsStored: number;
  };
  
  cloudUsage: {
    sttRequests: number;
    nlpRequests: number;
    ttsRequests: number;
    lastCloudRequest: Date;
  };
  
  consentStatus: PrivacyConsent;
  
  actions: {
    exportData(): Promise<Blob>;
    deleteAllData(): Promise<void>;
    revokeCloudConsent(): Promise<void>;
    viewProcessingLog(): ProcessingLogEntry[];
  };
}
```

## Third-Party Data Sharing

### Cloud Service Providers

#### OpenAI (Whisper, GPT-4o)
- **Data Sent**: Voice recordings (if enabled), text prompts
- **Purpose**: Speech recognition, intent parsing
- **Retention**: Per OpenAI's data retention policy
- **Control**: Can be disabled in settings

#### Hugging Face
- **Data Sent**: Document text (if enabled)
- **Purpose**: Document summarization
- **Retention**: Per Hugging Face's policy
- **Control**: Can be disabled in settings

#### No Data Sharing
- **Analytics**: No usage analytics sent to third parties
- **Telemetry**: No telemetry data collection
- **Advertising**: No data used for advertising purposes
- **Profiling**: No user profiling or behavioral analysis

## Privacy by Design Implementation

### Proactive Measures
- **Default Privacy Settings**: Most privacy-protective settings by default
- **Minimal Data Collection**: Only collect data necessary for functionality
- **Purpose Specification**: Clear purpose for each data collection
- **Use Limitation**: Data used only for specified purposes

### Technical Measures
```typescript
// Privacy-preserving settings defaults
const DEFAULT_PRIVACY_SETTINGS = {
  sttProvider: 'vosk',        // Local by default
  allowCloudNLP: false,       // Cloud disabled by default
  ttsProvider: 'system',      // Local by default
  logLevel: 'ERROR',          // Minimal logging
  dataRetention: 0,           // No persistent storage
  analyticsEnabled: false,    // No analytics
  crashReporting: false       // No crash reporting
};
```

### Organizational Measures
- **Privacy Training**: Regular privacy training for developers
- **Data Protection Officer**: Designated privacy contact
- **Privacy Impact Assessments**: Regular privacy reviews
- **Incident Response**: Privacy breach response procedures

## Contact Information

### Privacy Inquiries
- **Email**: privacy@aura-assistant.com
- **Response Time**: Within 72 hours
- **Languages**: English, Spanish, French, German

### Data Protection Officer
- **Contact**: dpo@aura-assistant.com
- **Role**: Privacy compliance and user rights
- **Availability**: Business hours (9 AM - 5 PM UTC)

## Updates to Privacy Policy

### Notification Process
- **Material Changes**: 30-day advance notice
- **Minor Updates**: Notification in application
- **Version Control**: All versions archived and accessible
- **User Consent**: Re-consent required for material changes

### Change Log
- **Version 1.0**: Initial privacy policy
- **Last Updated**: January 15, 2025
- **Next Review**: July 15, 2025