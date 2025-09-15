# Aura Desktop Assistant - Design Document

## Overview

Aura is a voice-first desktop assistant built with Tauri for cross-platform compatibility (Windows/Linux). The architecture follows a modular design with clear separation of concerns, utilizing XState for orchestration, GPT-4o for intent parsing, and local-first processing with optional cloud services.

## Architecture

### Component Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Tauri UI<br/>React/TypeScript]
        TTS[TTS Module<br/>OpenAI API]
        STT[STT Module<br/>Whisper Local]
    end
    
    subgraph "Orchestration Layer"
        ORCH[Orchestrator<br/>XState Machine]
        PARSER[Intent Parser<br/>GPT-4o Function Calling]
    end
    
    subgraph "Backend Services"
        API[FastAPI Backend<br/>Python Skills]
        FILE[File Operations<br/>Service]
        SHEET[Spreadsheet Analysis<br/>Pandas Service]
        DOC[Document AI<br/>HuggingFace Client]
        DATA[Data Entry Automation<br/>OCR & AI Service]
        EMAIL[Email Management<br/>IMAP/SMTP Service]
        CAL[Calendar Integration<br/>CalDAV/Exchange Service]
        REPORT[Report Generation<br/>Template Engine]
        WORKFLOW[Document Workflow<br/>Processing Service]
    end
    
    subgraph "Infrastructure"
        CONFIG[Config Manager<br/>Settings & Secrets]
        LOG[Logging Service<br/>Structured Logs]
        STORE[Local Storage<br/>SQLite/Files]
    end
    
    UI --> ORCH
    STT --> ORCH
    ORCH --> PARSER
    ORCH --> TTS
    PARSER --> ORCH
    ORCH --> API
    API --> FILE
    API --> SHEET
    API --> DOC
    API --> DATA
    API --> EMAIL
    API --> CAL
    API --> REPORT
    API --> WORKFLOW
    CONFIG --> API
    CONFIG --> PARSER
    LOG --> API
    LOG --> ORCH
    STORE --> API
```

### System Architecture Layers

1. **Frontend Layer**: Tauri-based UI with voice I/O capabilities
2. **Orchestration Layer**: XState-managed workflow and intent processing
3. **Backend Services**: FastAPI-based microservices for core functionality
4. **Infrastructure**: Configuration, logging, and data persistence

## Sequence Diagrams

### Flow 1: Create File and Write Text

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant STT
    participant Orchestrator
    participant Parser
    participant FileService
    participant TTS
    
    User->>UI: Voice: "Create file report.txt and write Hello World"
    UI->>STT: Audio stream
    STT->>Orchestrator: "Create file report.txt and write Hello World"
    Orchestrator->>Parser: Parse intent with context
    Parser->>Orchestrator: {action: "file_create_write", file: "report.txt", content: "Hello World"}
    Orchestrator->>FileService: create_and_write(path, content)
    FileService->>Orchestrator: Success response
    Orchestrator->>TTS: "File report.txt created successfully with your content"
    TTS->>UI: Audio response
    UI->>User: Voice + Visual confirmation
```

### Flow 2: Analyze Spreadsheet Salary Column Sum

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant STT
    participant Orchestrator
    participant Parser
    participant SpreadsheetService
    participant TTS
    
    User->>UI: Voice: "Sum the Salary column in employees.csv"
    UI->>STT: Audio stream
    STT->>Orchestrator: "Sum the Salary column in employees.csv"
    Orchestrator->>Parser: Parse intent with context
    Parser->>Orchestrator: {action: "spreadsheet_sum", file: "employees.csv", column: "Salary"}
    Orchestrator->>SpreadsheetService: calculate_sum(file, column)
    SpreadsheetService->>SpreadsheetService: Load CSV with pandas
    SpreadsheetService->>SpreadsheetService: df['Salary'].sum()
    SpreadsheetService->>Orchestrator: {result: 125000, count: 25}
    Orchestrator->>TTS: "The total salary is $125,000 across 25 employees"
    TTS->>UI: Audio response
    UI->>User: Voice + Visual chart/summary
```

### Flow 3: Summarize PDF in 3 Bullets

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant STT
    participant Orchestrator
    participant Parser
    participant DocumentService
    participant HFClient
    participant TTS
    
    User->>UI: Voice: "Summarize report.pdf in 3 bullet points"
    UI->>STT: Audio stream
    STT->>Orchestrator: "Summarize report.pdf in 3 bullet points"
    Orchestrator->>Parser: Parse intent with context
    Parser->>Orchestrator: {action: "document_summarize", file: "report.pdf", format: "bullets", count: 3}
    Orchestrator->>DocumentService: summarize_pdf(file, bullets=3)
    DocumentService->>DocumentService: Extract text from PDF
    DocumentService->>HFClient: Summarization request
    HFClient->>DocumentService: Summary response
    DocumentService->>Orchestrator: {summary: ["Point 1", "Point 2", "Point 3"]}
    Orchestrator->>TTS: "Here are 3 key points: 1. Point 1, 2. Point 2, 3. Point 3"
    TTS->>UI: Audio response
    UI->>User: Voice + Visual bullet list
```

### Flow 4: Automate Invoice Data Extraction

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant STT
    participant Orchestrator
    participant Parser
    participant DataService
    participant OCREngine
    participant WorkflowService
    participant TTS
    
    User->>UI: Voice: "Extract data from invoice.pdf and add to expenses spreadsheet"
    UI->>STT: Audio stream
    STT->>Orchestrator: "Extract data from invoice.pdf and add to expenses spreadsheet"
    Orchestrator->>Parser: Parse intent with context
    Parser->>Orchestrator: {action: "data_extract_transfer", source: "invoice.pdf", destination: "expenses.xlsx"}
    Orchestrator->>DataService: extract_invoice_data(file)
    DataService->>OCREngine: Process PDF with OCR
    OCREngine->>DataService: Raw text and layout
    DataService->>DataService: AI extraction of vendor, amount, date, items
    DataService->>Orchestrator: {vendor: "ABC Corp", amount: 1250.00, date: "2024-01-15", items: [...]}
    Orchestrator->>WorkflowService: add_to_spreadsheet(data, "expenses.xlsx")
    WorkflowService->>Orchestrator: Success with row number
    Orchestrator->>TTS: "Invoice data extracted: $1,250 from ABC Corp added to row 45 of expenses spreadsheet"
    TTS->>UI: Audio response
    UI->>User: Voice + Visual data summary
```

### Flow 5: Schedule Multi-Participant Meeting

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant STT
    participant Orchestrator
    participant Parser
    participant CalendarService
    participant EmailService
    participant TTS
    
    User->>UI: Voice: "Schedule 1-hour meeting with John and Sarah next week"
    UI->>STT: Audio stream
    STT->>Orchestrator: "Schedule 1-hour meeting with John and Sarah next week"
    Orchestrator->>Parser: Parse intent with context
    Parser->>Orchestrator: {action: "schedule_meeting", participants: ["John", "Sarah"], duration: 60, timeframe: "next_week"}
    Orchestrator->>CalendarService: find_available_slots(participants, duration, timeframe)
    CalendarService->>CalendarService: Check all calendars for conflicts
    CalendarService->>Orchestrator: {slots: ["Mon 2PM-3PM", "Wed 10AM-11AM", "Fri 3PM-4PM"]}
    Orchestrator->>TTS: "Found 3 available slots: Monday 2-3PM, Wednesday 10-11AM, Friday 3-4PM. Which works best?"
    TTS->>UI: Audio response with slot options
    UI->>User: Voice + Visual calendar slots
    User->>UI: "Wednesday 10AM"
    UI->>Orchestrator: Selected slot
    Orchestrator->>CalendarService: book_meeting(slot, participants)
    CalendarService->>EmailService: send_invitations(meeting_details)
    EmailService->>Orchestrator: Invitations sent
    Orchestrator->>TTS: "Meeting scheduled for Wednesday 10-11AM. Invitations sent to John and Sarah."
    TTS->>UI: Audio confirmation
```

### Flow 6: Generate Weekly Sales Report

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant STT
    participant Orchestrator
    participant Parser
    participant ReportService
    participant DataSources
    participant EmailService
    participant TTS
    
    User->>UI: Voice: "Generate this week's sales report and email to the team"
    UI->>STT: Audio stream
    STT->>Orchestrator: "Generate this week's sales report and email to the team"
    Orchestrator->>Parser: Parse intent with context
    Parser->>Orchestrator: {action: "generate_report", type: "sales", period: "this_week", distribute: "team"}
    Orchestrator->>ReportService: generate_sales_report(period="this_week")
    ReportService->>DataSources: Fetch sales data from CRM, spreadsheets
    DataSources->>ReportService: Raw sales data
    ReportService->>ReportService: Process data, apply template, generate charts
    ReportService->>Orchestrator: {report_file: "sales_report_2024_w04.pdf", metrics: {...}}
    Orchestrator->>EmailService: send_report(file, recipients="team")
    EmailService->>Orchestrator: Email sent successfully
    Orchestrator->>TTS: "Weekly sales report generated showing $45K revenue, 23% increase. Emailed to team."
    TTS->>UI: Audio response
    UI->>User: Voice + Visual report preview
```

## State Machine Design

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Capture : Voice/Text Input
    Capture --> ParseIntent : Input Complete
    ParseIntent --> Route : Intent Parsed
    ParseIntent --> Capture : Parse Failed/Clarification Needed
    
    Route --> Execute : Valid Intent
    Route --> Idle : Invalid Intent
    
    Execute --> Verify : Operation Complete
    Execute --> Route : Execution Failed
    
    Verify --> Respond : Verification Passed
    Verify --> Execute : Retry Needed
    
    Respond --> Idle : Response Delivered
    
    state Capture {
        [*] --> ListeningVoice
        ListeningVoice --> ProcessingSTT : Voice Complete
        ProcessingSTT --> [*] : Text Ready
        
        [*] --> TextInput
        TextInput --> [*] : Text Submitted
    }
    
    state Execute {
        [*] --> FileOps
        [*] --> SpreadsheetOps
        [*] --> DocumentAI
        [*] --> DataAutomation
        [*] --> EmailAutomation
        [*] --> CalendarAutomation
        [*] --> ReportGeneration
        [*] --> WorkflowProcessing
        FileOps --> [*]
        SpreadsheetOps --> [*]
        DocumentAI --> [*]
        DataAutomation --> [*]
        EmailAutomation --> [*]
        CalendarAutomation --> [*]
        ReportGeneration --> [*]
        WorkflowProcessing --> [*]
    }
```

## Components and Interfaces

### Core Components

#### 1. Tauri UI Layer
- **Technology**: React + TypeScript + Tauri
- **Responsibilities**: User interface, voice I/O coordination, visual feedback
- **Interfaces**: 
  - `VoiceInterface`: STT/TTS management
  - `UIStateManager`: React state synchronization with XState

#### 2. Orchestrator (XState)
- **Technology**: XState v5
- **Responsibilities**: Workflow management, state transitions, error handling
- **Interfaces**:
  - `StateMachine`: Core state management
  - `EventBus`: Inter-component communication

#### 3. Intent Parser
- **Technology**: GPT-4o Function Calling
- **Responsibilities**: Natural language understanding, command parsing
- **Interfaces**:
  - `IntentParser`: Parse user input to structured commands
  - `FunctionSchema`: Strict JSON schema definitions

#### 4. Backend Services (FastAPI)
- **Technology**: FastAPI + Python
- **Responsibilities**: Business logic execution, data processing
- **Services**:
  - `FileOperationsService`: File system interactions
  - `SpreadsheetService`: Pandas-based data analysis
  - `DocumentAIService`: PDF processing and AI integration
  - `DataAutomationService`: OCR and data extraction/transfer
  - `EmailManagementService`: IMAP/SMTP email processing and automation
  - `CalendarService`: Calendar integration and scheduling automation
  - `ReportGenerationService`: Automated report compilation and formatting
  - `WorkflowProcessingService`: Document workflow and approval routing

#### 5. STT/TTS Modules
- **STT**: Whisper (local processing)
- **TTS**: OpenAI TTS API
- **Interfaces**:
  - `SpeechToText`: Audio → Text conversion
  - `TextToSpeech`: Text → Audio conversion

## Data Models

### Intent Schema
```typescript
interface ParsedIntent {
  action: 'file_create' | 'file_write' | 'spreadsheet_analyze' | 'document_summarize' | 
          'data_extract' | 'data_transfer' | 'email_sort' | 'email_respond' | 
          'schedule_meeting' | 'calendar_check' | 'generate_report' | 'process_workflow';
  parameters: {
    // File operations
    file?: string;
    content?: string;
    
    // Spreadsheet operations
    column?: string;
    operation?: 'sum' | 'average' | 'find';
    
    // Document operations
    format?: 'bullets' | 'paragraph';
    count?: number;
    
    // Data automation
    source?: string;
    destination?: string;
    extractionType?: 'invoice' | 'contract' | 'form' | 'receipt';
    
    // Email automation
    emailRules?: EmailRule[];
    templateId?: string;
    recipients?: string[];
    
    // Calendar automation
    participants?: string[];
    duration?: number;
    timeframe?: string;
    meetingType?: 'internal' | 'client' | 'interview';
    
    // Report generation
    reportType?: 'sales' | 'financial' | 'performance' | 'custom';
    period?: 'daily' | 'weekly' | 'monthly' | 'quarterly';
    dataSources?: string[];
    
    // Workflow processing
    workflowType?: 'approval' | 'review' | 'routing';
    approvers?: string[];
    priority?: 'low' | 'medium' | 'high' | 'urgent';
  };
  confidence: number;
  context?: string;
}

interface EmailRule {
  condition: string;
  action: 'move' | 'label' | 'forward' | 'respond';
  target: string;
}
```

### State Context
```typescript
interface AuraContext {
  currentInput: string;
  parsedIntent?: ParsedIntent;
  executionResult?: any;
  errorState?: ErrorInfo;
  userPreferences: UserConfig;
  sessionHistory: ConversationTurn[];
}
```

### Configuration Model
```typescript
interface AuraConfig {
  voice: {
    sttEnabled: boolean;
    ttsEnabled: boolean;
    language: string;
  };
  privacy: {
    cloudServicesEnabled: boolean;
    dataRetention: number;
  };
  services: {
    openaiApiKey?: string;
    huggingfaceApiKey?: string;
  };
}
```

## Automation Architecture

### Data Processing Pipeline

```mermaid
flowchart TD
    A[Document Input] --> B{Document Type Detection}
    B -->|Invoice| C[Invoice OCR Engine]
    B -->|Contract| D[Contract AI Parser]
    B -->|Form| E[Form Field Extractor]
    B -->|Email| F[Email Content Analyzer]
    
    C --> G[Data Validation]
    D --> G
    E --> G
    F --> G
    
    G --> H{Validation Passed?}
    H -->|Yes| I[Structured Data Output]
    H -->|No| J[Manual Review Queue]
    
    I --> K[Destination Routing]
    K --> L[CRM Integration]
    K --> M[Spreadsheet Update]
    K --> N[Database Insert]
    K --> O[Workflow Trigger]
```

### Email Automation Flow

```mermaid
flowchart TD
    A[Incoming Email] --> B[Content Analysis]
    B --> C[Intent Classification]
    C --> D{Rule Match?}
    
    D -->|Yes| E[Apply Automation Rule]
    D -->|No| F[Smart Suggestion]
    
    E --> G[Execute Action]
    G --> H[Move to Folder]
    G --> I[Send Auto-Reply]
    G --> J[Create Calendar Event]
    G --> K[Forward to Team]
    
    F --> L[Present Options to User]
    L --> M[Learn from User Choice]
```

### Calendar Scheduling Algorithm

```mermaid
flowchart TD
    A[Meeting Request] --> B[Parse Participants]
    B --> C[Fetch All Calendars]
    C --> D[Identify Busy Times]
    D --> E[Calculate Free Slots]
    E --> F{Conflicts Found?}
    
    F -->|No| G[Propose Optimal Times]
    F -->|Yes| H[Conflict Resolution]
    
    H --> I[Alternative Time Suggestions]
    H --> J[Priority-Based Scheduling]
    H --> K[Partial Availability Options]
    
    G --> L[Send Calendar Invites]
    I --> L
    J --> L
    K --> L
    
    L --> M[Track Responses]
    M --> N[Confirm Final Meeting]
```

## Technology Tradeoffs

### Tauri vs Electron

**Chosen: Tauri**

**Pros:**
- Smaller bundle size (~10MB vs ~100MB)
- Better performance (Rust backend)
- Lower memory footprint
- Native OS integration
- Better security model

**Cons:**
- Smaller ecosystem
- Rust learning curve for backend
- Less mature tooling

**Alternative Considered:** Electron would provide larger ecosystem and easier JavaScript development but at the cost of performance and resource usage.

### GPT-4o vs Local NLP

**Chosen: GPT-4o with Local Fallback**

**Pros:**
- Superior intent understanding
- Function calling capabilities
- Handles complex, ambiguous queries
- Regular model improvements

**Cons:**
- Requires internet connectivity
- API costs
- Privacy considerations
- Latency for cloud calls

**Alternative Considered:** Local models (spaCy, transformers) would provide privacy and offline capability but with significantly reduced accuracy for complex intent parsing.

### OCR Engine Selection

**Chosen: Tesseract + PaddleOCR Hybrid**

**Pros:**
- Tesseract: Excellent for typed text, open source, mature
- PaddleOCR: Superior for handwritten text, table detection
- Combined approach maximizes accuracy across document types
- Local processing maintains privacy

**Cons:**
- Larger model footprint
- Requires GPU for optimal PaddleOCR performance
- More complex integration

**Alternative Considered:** Cloud OCR services (Google Vision, AWS Textract) would provide higher accuracy but compromise privacy and require internet connectivity.

### Email Integration Approach

**Chosen: IMAP/SMTP with OAuth 2.0**

**Pros:**
- Universal compatibility with email providers
- Secure authentication without password storage
- Real-time email processing capability
- Granular permission control

**Cons:**
- Complex OAuth setup for multiple providers
- Rate limiting considerations
- Requires internet connectivity

**Alternative Considered:** Exchange Web Services (EWS) would provide deeper Outlook integration but limit compatibility with other email providers.

### Calendar Integration Strategy

**Chosen: CalDAV + Exchange Web Services**

**Pros:**
- CalDAV: Universal standard, works with most calendar systems
- EWS: Deep Outlook/Exchange integration for enterprise users
- Covers majority of business calendar scenarios
- Supports real-time availability checking

**Cons:**
- Dual integration complexity
- Different authentication methods
- Varying feature support across providers

**Alternative Considered:** Google Calendar API only would be simpler but exclude many enterprise users.

### Whisper vs Vosk

**Chosen: Whisper (Local)**

**Pros:**
- State-of-the-art accuracy
- Multi-language support
- Robust to accents/noise
- Local processing (privacy)

**Cons:**
- Larger model size
- Higher computational requirements
- Slower than cloud alternatives

**Alternative Considered:** Vosk would be lighter and faster but with reduced accuracy, especially for technical terminology.

## Data Flow & Privacy

### Data Flow Architecture

```mermaid
flowchart TD
    A[User Voice Input] --> B[Local STT Processing]
    B --> C[Local State Management]
    C --> D{Cloud Services Enabled?}
    
    D -->|Yes| E[Encrypted API Call]
    D -->|No| F[Local Processing Only]
    
    E --> G[Intent Parsing - GPT-4o]
    F --> H[Basic Pattern Matching]
    
    G --> I[Local Execution]
    H --> I
    
    I --> J[Local Storage]
    I --> K[TTS Response]
    
    K --> L[User Audio Output]
    
    style B fill:#90EE90
    style C fill:#90EE90
    style F fill:#90EE90
    style I fill:#90EE90
    style J fill:#90EE90
    style E fill:#FFB6C1
    style G fill:#FFB6C1
```

### Privacy Design Principles

#### 1. Local-First Processing
- **Voice Data**: All STT processing happens locally using Whisper
- **File Operations**: Direct local file system access, no cloud storage
- **Spreadsheet Analysis**: Local pandas processing, data never leaves device
- **State Management**: XState runs entirely locally

#### 2. Explicit Cloud Consent
- **Intent Parsing**: GPT-4o calls only with user permission
- **Document AI**: HuggingFace API calls require explicit consent
- **TTS**: OpenAI TTS with user awareness and opt-out capability

#### 3. Data Minimization
- **API Calls**: Only send necessary context, not full documents
- **Logging**: Structured logs with PII filtering
- **Storage**: Minimal local storage with automatic cleanup
- **Session Data**: Conversation history with configurable retention

#### 4. Security Measures
- **API Keys**: Stored in encrypted local configuration
- **Network**: HTTPS for all external communications
- **File Access**: Sandboxed file operations within user directories
- **Error Handling**: No sensitive data in error messages or logs
- **Email Security**: OAuth tokens encrypted at rest, minimal scope permissions
- **Document Processing**: Malware scanning before OCR processing
- **Calendar Access**: Read-only by default, explicit write permissions
- **Data Transfer**: Validation and sanitization for all automated data transfers

### Privacy Controls

```typescript
interface PrivacySettings {
  cloudServices: {
    intentParsing: boolean;
    documentAI: boolean;
    ttsService: boolean;
    ocrProcessing: boolean;
  };
  dataRetention: {
    conversationHistory: number; // days
    logFiles: number; // days
    tempFiles: number; // hours
    extractedData: number; // days
    emailCache: number; // days
    calendarCache: number; // days
    fileVersions: number; // days or version count
    commandHistory: number; // days or command count
  };
  security: {
    encryptLocalData: boolean;
    requireConfirmation: boolean;
    auditLogging: boolean;
    encryptVersions: boolean;
    secureVersionDeletion: boolean;
  };
  automation: {
    emailAccess: boolean;
    calendarAccess: boolean;
    documentProcessing: boolean;
    dataTransfer: boolean;
    reportGeneration: boolean;
    workflowAutomation: boolean;
  };
  permissions: {
    fileSystemAccess: string[]; // allowed directories
    emailAccounts: string[]; // authorized email accounts
    calendarSources: string[]; // authorized calendar sources
    externalIntegrations: string[]; // CRM, databases, etc.
  };
  versioning: {
    enableAutoVersioning: boolean;
    maxVersionsPerFile: number;
    maxStorageSize: number; // MB
    enableDifferentialVersioning: boolean;
    autoCleanupEnabled: boolean;
  };
}
```

## State Management and Versioning Architecture

### Versioning System Design

```mermaid
flowchart TD
    A[User Action] --> B[Pre-Operation Hook]
    B --> C[Create File Version]
    C --> D[Execute Operation]
    D --> E[Log Command History]
    E --> F[Update State]
    
    C --> G[.aura/versions/]
    E --> H[.aura/history/]
    F --> I[.aura/state/]
    
    G --> J[File Backup]
    G --> K[Metadata Storage]
    G --> L[Differential Storage]
    
    H --> M[Command Log]
    H --> N[Execution Context]
    H --> O[Result Tracking]
    
    I --> P[Application State]
    I --> Q[Session Context]
    I --> R[Recovery Points]
```

### .aura Directory Structure

```
.aura/
├── versions/                    # File versioning system
│   ├── {file_path_hash}/       # Hashed file path directory
│   │   ├── {timestamp_1}/      # Version timestamp
│   │   │   ├── content         # File content
│   │   │   ├── metadata.json   # Version metadata
│   │   │   └── diff.patch      # Differential changes
│   │   └── {timestamp_2}/
│   └── index.json              # Version index and lookup
├── history/                    # Command and execution history
│   ├── commands.jsonl          # Command execution log
│   ├── sessions/               # Session-based history
│   │   └── {session_id}.json   # Session command history
│   └── index.json              # History index and search
├── state/                      # Application state management
│   ├── checkpoints/            # State checkpoints
│   ├── recovery/               # Recovery points
│   └── current.json            # Current application state
├── config/                     # Versioning configuration
│   ├── retention.json          # Retention policies
│   ├── storage.json            # Storage settings
│   └── security.json           # Security configuration
└── logs/                       # System logs
    ├── versioning.log          # Versioning operations
    ├── cleanup.log             # Cleanup operations
    └── errors.log              # Error tracking
```

### Versioning Data Models

```typescript
interface FileVersion {
  id: string;
  filePath: string;
  timestamp: Date;
  size: number;
  checksum: string;
  changeDescription: string;
  operationType: 'create' | 'modify' | 'delete';
  commandId: string;
  metadata: {
    originalSize: number;
    compressionRatio: number;
    isDifferential: boolean;
    parentVersion?: string;
  };
}

interface CommandHistoryEntry {
  id: string;
  timestamp: Date;
  sessionId: string;
  userInput: string;
  parsedIntent: ParsedIntent;
  executionDuration: number;
  success: boolean;
  errorMessage?: string;
  affectedFiles: string[];
  beforeState: Record<string, any>;
  afterState: Record<string, any>;
  rollbackData?: RollbackData;
}

interface RollbackData {
  operationType: string;
  affectedFiles: FileRollbackInfo[];
  stateChanges: StateChange[];
  dependencies: string[]; // Other commands that depend on this
}

interface FileRollbackInfo {
  filePath: string;
  beforeVersion: string;
  afterVersion: string;
  operation: 'created' | 'modified' | 'deleted';
}

interface StateCheckpoint {
  id: string;
  timestamp: Date;
  description: string;
  applicationState: Record<string, any>;
  fileStates: Record<string, string>; // file path -> version id
  commandCount: number;
  isAutomatic: boolean;
}
```

### Rollback System Architecture

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant RollbackService
    participant VersionManager
    participant FileSystem
    participant StateManager
    
    User->>UI: Request rollback to timestamp
    UI->>RollbackService: initiate_rollback(timestamp)
    RollbackService->>VersionManager: analyze_impact(timestamp)
    VersionManager->>RollbackService: affected_files_and_operations
    RollbackService->>UI: show_rollback_preview(changes)
    UI->>User: Display preview and confirmation
    User->>UI: Confirm rollback
    UI->>RollbackService: execute_rollback()
    
    loop For each affected file
        RollbackService->>VersionManager: get_version_at_timestamp(file, timestamp)
        VersionManager->>FileSystem: restore_file_version(file, version)
    end
    
    RollbackService->>StateManager: restore_application_state(timestamp)
    StateManager->>RollbackService: state_restored
    RollbackService->>VersionManager: create_rollback_checkpoint()
    RollbackService->>UI: rollback_complete(summary)
    UI->>User: Show rollback results
```
```

## Error Handling

### Error Categories
1. **Voice Processing Errors**: STT failures, audio device issues
2. **Intent Parsing Errors**: Ambiguous commands, API failures
3. **Execution Errors**: File access denied, network timeouts
4. **System Errors**: State corruption, service unavailability

### Recovery Strategies
- **Graceful Degradation**: Fall back to text mode when voice fails
- **Retry Logic**: Exponential backoff for transient failures
- **User Guidance**: Clear error messages with suggested actions
- **State Recovery**: XState error states with recovery transitions

## Testing Strategy

### Unit Testing
- **Component Tests**: React components with Jest/RTL
- **Service Tests**: FastAPI endpoints with pytest
- **State Machine Tests**: XState machine behavior verification

### Integration Testing
- **Voice Flow Tests**: End-to-end voice command processing
- **API Integration**: External service integration testing
- **Cross-Platform Tests**: Windows/Linux compatibility verification

### Performance Testing
- **Voice Latency**: STT/TTS response time measurement
- **Memory Usage**: Resource consumption monitoring
- **File Processing**: Large file handling performance

This design provides a robust, privacy-focused architecture that balances local processing with cloud capabilities while maintaining user control and system reliability.