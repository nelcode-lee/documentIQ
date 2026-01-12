/** Translation strings for multi-language support. */

export type Language = 'en' | 'pl' | 'ro';

export interface Translations {
  // Common
  chat: string;
  documents: string;
  upload: string;
  generate: string;
  analytics: string;
  send: string;
  clear: string;
  loading: string;
  error: string;
  
  // Chat page
  chatTitle: string;
  chatSubtitle: string;
  startConversation: string;
  startConversationSubtitle: string;
  typeMessage: string;
  thinking: string;
  clearChat: string;
  popularQuestions: string;
  mostPopularQuestions: string;
  poweredBy: string;
  language: string;
  defaultQuestions: string[];
  greeting: string;
  greetingSubtitle: string;
  howToUse: string;
  examplePrompts: string;
  tipsForBetterQueries: string;
  tipBeSpecific: string;
  tipAskQuestions: string;
  tipRequestExamples: string;
  tipAskForSteps: string;
  examplePrompt1: string;
  examplePrompt2: string;
  examplePrompt3: string;
  close: string;
  
  // Documents page
  documentLibrary: string;
  manageDocuments: string;
  uploadNewDocument: string;
  searchDocuments: string;
  source: string;
  allSources: string;
  uploaded: string;
  generated: string;
  category: string;
  allCategories: string;
  sortBy: string;
  newestFirst: string;
  oldestFirst: string;
  titleAZ: string;
  categoryAZ: string;
  noDocumentsFound: string;
  tryAdjustingFilters: string;
  
  // Upload page
  uploadTitle: string;
  uploadSubtitle: string;
  dragDropFiles: string;
  orSelectFile: string;
  fileTypes: string;
  documentTitle: string;
  documentCategory: string;
  tags: string;
  uploadButton: string;
  uploading: string;
  
  // Generate page
  generateTitle: string;
  generateSubtitle: string;
  
  // Analytics page
  analyticsTitle: string;
  analyticsSubtitle: string;
  totalQueries: string;
  avgResponseTime: string;
  dailyQueries: string;
  documentsAccessed: string;
  queryVolume: string;
  averageResponseTime: string;
  mostAccessedDocuments: string;
  mostPopularQueries: string;
  
  // Status
  completed: string;
  processing: string;
  errorStatus: string;
}

export const translations: Record<Language, Translations> = {
  en: {
    chat: 'Chat',
    documents: 'Documents',
    upload: 'Upload',
    generate: 'Generate',
    analytics: 'Analytics',
    send: 'Send',
    clear: 'Clear',
    loading: 'Loading...',
    error: 'Error',
    
    chatTitle: 'Chat',
    chatSubtitle: 'Ask questions about your technical standards',
    startConversation: 'Start a conversation',
    startConversationSubtitle: 'Ask questions about your technical standards documents',
    typeMessage: 'Type your message...',
    thinking: 'Thinking...',
    clearChat: 'Clear Chat',
    popularQuestions: 'Popular Questions',
    mostPopularQuestions: 'Most Popular Questions',
    poweredBy: 'Powered by DocumentIQ',
    language: 'Language',
    defaultQuestions: [
      'What are the safety requirements for working at height?',
      'How do I complete a risk assessment?',
      'What are the quality control procedures?',
      'What personal protective equipment is required?',
      'How do I report an incident?',
    ],
    greeting: 'Welcome to DocumentIQ',
    greetingSubtitle: 'AI-powered document intelligence for technical standards, procedures, and documentation',
    howToUse: 'How to Get the Most Out of Your Queries',
    examplePrompts: 'Example Prompts',
    tipsForBetterQueries: 'Tips for Better Queries',
    tipBeSpecific: 'Be specific: Include context like document names, section numbers, or process names',
    tipAskQuestions: 'Ask questions: Use "what", "how", "when", "where", or "why" to get detailed answers',
    tipRequestExamples: 'Request examples: Ask for real-world examples or use cases',
    tipAskForSteps: 'Ask for steps: Request step-by-step procedures or processes',
    examplePrompt1: 'What are the safety requirements for working at height according to document X?',
    examplePrompt2: 'How do I complete a risk assessment step-by-step?',
    examplePrompt3: 'Can you provide an example of a HACCP validation process?',
    close: 'Close',
    
    documentLibrary: 'Document Library',
    manageDocuments: 'Manage your uploaded and generated technical standards documents.',
    uploadNewDocument: 'Upload New Document',
    searchDocuments: 'Search documents...',
    source: 'Source',
    allSources: 'All Sources',
    uploaded: 'Uploaded',
    generated: 'Generated',
    category: 'Category',
    allCategories: 'All Categories',
    sortBy: 'Sort By',
    newestFirst: 'Newest First',
    oldestFirst: 'Oldest First',
    titleAZ: 'Title (A-Z)',
    categoryAZ: 'Category (A-Z)',
    noDocumentsFound: 'No documents found',
    tryAdjustingFilters: 'Try adjusting your filters or',
    
    uploadTitle: 'Upload Document',
    uploadSubtitle: 'Upload and ingest technical standards documents',
    dragDropFiles: 'Drag and drop files here',
    orSelectFile: 'or select a file',
    fileTypes: 'Supported file types: PDF, DOCX, TXT',
    documentTitle: 'Document Title',
    documentCategory: 'Category',
    tags: 'Tags (comma-separated)',
    uploadButton: 'Upload Document',
    uploading: 'Uploading...',
    
    generateTitle: 'Generate Document',
    generateSubtitle: 'Generate new technical standards documents using AI',
    
    analyticsTitle: 'Analytics Dashboard',
    analyticsSubtitle: 'Insights into system usage and performance.',
    totalQueries: 'Total Queries',
    avgResponseTime: 'Avg. Response Time',
    dailyQueries: 'Daily Queries',
    documentsAccessed: 'Documents Accessed',
    queryVolume: 'Query Volume Over Time',
    averageResponseTime: 'Average Response Time',
    mostAccessedDocuments: 'Most Accessed Documents',
    mostPopularQueries: 'Most Popular Queries',
    
    completed: 'completed',
    processing: 'processing',
    errorStatus: 'error',
  },
  
  pl: {
    chat: 'Czat',
    documents: 'Dokumenty',
    upload: 'Prześlij',
    generate: 'Generuj',
    analytics: 'Analityka',
    send: 'Wyślij',
    clear: 'Wyczyść',
    loading: 'Ładowanie...',
    error: 'Błąd',
    
    chatTitle: 'Czat',
    chatSubtitle: 'Zadawaj pytania dotyczące standardów technicznych',
    startConversation: 'Rozpocznij rozmowę',
    startConversationSubtitle: 'Zadawaj pytania dotyczące dokumentów standardów technicznych',
    typeMessage: 'Wpisz wiadomość...',
    thinking: 'Myślę...',
    clearChat: 'Wyczyść czat',
    popularQuestions: 'Popularne pytania',
    mostPopularQuestions: 'Najpopularniejsze pytania',
    poweredBy: 'Zasilane przez Cranswick Group IT - Automatyzacja',
    language: 'Język',
    defaultQuestions: [
      'Jakie są wymagania bezpieczeństwa dotyczące pracy na wysokości?',
      'Jak wypełnić ocenę ryzyka?',
      'Jakie są procedury kontroli jakości?',
      'Jakie środki ochrony osobistej są wymagane?',
      'Jak zgłosić incydent?',
    ],
    greeting: 'Witamy w DocumentIQ',
    greetingSubtitle: 'System inteligencji dokumentów wspierany przez AI dla standardów technicznych, procedur i dokumentacji',
    howToUse: 'Jak najlepiej wykorzystać swoje zapytania',
    examplePrompts: 'Przykładowe pytania',
    tipsForBetterQueries: 'Wskazówki dotyczące lepszych zapytań',
    tipBeSpecific: 'Bądź konkretny: Uwzględnij kontekst, takie jak nazwy dokumentów, numery sekcji lub nazwy procesów',
    tipAskQuestions: 'Zadawaj pytania: Używaj "co", "jak", "kiedy", "gdzie" lub "dlaczego", aby uzyskać szczegółowe odpowiedzi',
    tipRequestExamples: 'Poproś o przykłady: Poproś o przykłady z rzeczywistego świata lub przypadki użycia',
    tipAskForSteps: 'Poproś o kroki: Poproś o procedury krok po kroku lub procesy',
    examplePrompt1: 'Jakie są wymagania bezpieczeństwa dotyczące pracy na wysokości zgodnie z dokumentem X?',
    examplePrompt2: 'Jak krok po kroku wypełnić ocenę ryzyka?',
    examplePrompt3: 'Czy możesz podać przykład procesu walidacji HACCP?',
    close: 'Zamknij',
    
    documentLibrary: 'Biblioteka dokumentów',
    manageDocuments: 'Zarządzaj przesłanymi i wygenerowanymi dokumentami standardów technicznych.',
    uploadNewDocument: 'Prześlij nowy dokument',
    searchDocuments: 'Szukaj dokumentów...',
    source: 'Źródło',
    allSources: 'Wszystkie źródła',
    uploaded: 'Przesłane',
    generated: 'Wygenerowane',
    category: 'Kategoria',
    allCategories: 'Wszystkie kategorie',
    sortBy: 'Sortuj według',
    newestFirst: 'Najnowsze najpierw',
    oldestFirst: 'Najstarsze najpierw',
    titleAZ: 'Tytuł (A-Z)',
    categoryAZ: 'Kategoria (A-Z)',
    noDocumentsFound: 'Nie znaleziono dokumentów',
    tryAdjustingFilters: 'Spróbuj dostosować filtry lub',
    
    uploadTitle: 'Prześlij dokument',
    uploadSubtitle: 'Prześlij i wprowadź dokumenty standardów technicznych',
    dragDropFiles: 'Przeciągnij i upuść pliki tutaj',
    orSelectFile: 'lub wybierz plik',
    fileTypes: 'Obsługiwane typy plików: PDF, DOCX, TXT',
    documentTitle: 'Tytuł dokumentu',
    documentCategory: 'Kategoria',
    tags: 'Tagi (oddzielone przecinkami)',
    uploadButton: 'Prześlij dokument',
    uploading: 'Przesyłanie...',
    
    generateTitle: 'Generuj dokument',
    generateSubtitle: 'Generuj nowe dokumenty standardów technicznych przy użyciu AI',
    
    analyticsTitle: 'Pulpit analityczny',
    analyticsSubtitle: 'Wgląd w użycie systemu i wydajność.',
    totalQueries: 'Łączne zapytania',
    avgResponseTime: 'Średni czas odpowiedzi',
    dailyQueries: 'Zapytania dzienne',
    documentsAccessed: 'Dokumenty dostępne',
    queryVolume: 'Wolumen zapytań w czasie',
    averageResponseTime: 'Średni czas odpowiedzi',
    mostAccessedDocuments: 'Najczęściej dostępne dokumenty',
    mostPopularQueries: 'Najpopularniejsze zapytania',
    
    completed: 'zakończone',
    processing: 'przetwarzanie',
    errorStatus: 'błąd',
  },
  
  ro: {
    chat: 'Chat',
    documents: 'Documente',
    upload: 'Încărcare',
    generate: 'Generare',
    analytics: 'Analiză',
    send: 'Trimite',
    clear: 'Șterge',
    loading: 'Se încarcă...',
    error: 'Eroare',
    
    chatTitle: 'Chat',
    chatSubtitle: 'Pune întrebări despre standardele tehnice',
    startConversation: 'Începe o conversație',
    startConversationSubtitle: 'Pune întrebări despre documentele standardelor tehnice',
    typeMessage: 'Scrie mesajul...',
    thinking: 'Mă gândesc...',
    clearChat: 'Șterge chat-ul',
    popularQuestions: 'Întrebări populare',
    mostPopularQuestions: 'Cele mai populare întrebări',
    poweredBy: 'Alimentat de Cranswick Group IT - Automatizare',
    language: 'Limba',
    defaultQuestions: [
      'Care sunt cerințele de siguranță pentru lucrul la înălțime?',
      'Cum completez o evaluare a riscului?',
      'Care sunt procedurile de control al calității?',
      'Ce echipament individual de protecție este necesar?',
      'Cum raportez un incident?',
    ],
    greeting: 'Bun venit la DocumentIQ',
    greetingSubtitle: 'Sistem de inteligență a documentelor alimentat de AI pentru standarde tehnice, proceduri și documentație',
    howToUse: 'Cum să obții cele mai bune rezultate din interogările tale',
    examplePrompts: 'Întrebări de exemplu',
    tipsForBetterQueries: 'Sfaturi pentru interogări mai bune',
    tipBeSpecific: 'Fii specific: Include context precum nume de documente, numere de secțiuni sau nume de procese',
    tipAskQuestions: 'Pune întrebări: Folosește "ce", "cum", "când", "unde" sau "de ce" pentru a obține răspunsuri detaliate',
    tipRequestExamples: 'Solicită exemple: Cere exemple din lumea reală sau cazuri de utilizare',
    tipAskForSteps: 'Cere pași: Solicită proceduri pas cu pas sau procese',
    examplePrompt1: 'Care sunt cerințele de siguranță pentru lucrul la înălțime conform documentului X?',
    examplePrompt2: 'Cum completez o evaluare a riscului pas cu pas?',
    examplePrompt3: 'Poți oferi un exemplu de proces de validare HACCP?',
    close: 'Închide',
    
    documentLibrary: 'Biblioteca de documente',
    manageDocuments: 'Gestionează documentele standardelor tehnice încărcate și generate.',
    uploadNewDocument: 'Încarcă document nou',
    searchDocuments: 'Caută documente...',
    source: 'Sursă',
    allSources: 'Toate sursele',
    uploaded: 'Încărcate',
    generated: 'Generate',
    category: 'Categorie',
    allCategories: 'Toate categoriile',
    sortBy: 'Sortează după',
    newestFirst: 'Cele mai noi primele',
    oldestFirst: 'Cele mai vechi primele',
    titleAZ: 'Titlu (A-Z)',
    categoryAZ: 'Categorie (A-Z)',
    noDocumentsFound: 'Nu s-au găsit documente',
    tryAdjustingFilters: 'Încearcă să ajustezi filtrele sau',
    
    uploadTitle: 'Încarcă document',
    uploadSubtitle: 'Încarcă și integrează documente standarde tehnice',
    dragDropFiles: 'Trage și plasează fișierele aici',
    orSelectFile: 'sau selectează un fișier',
    fileTypes: 'Tipuri de fișiere suportate: PDF, DOCX, TXT',
    documentTitle: 'Titlul documentului',
    documentCategory: 'Categorie',
    tags: 'Etichete (separate prin virgulă)',
    uploadButton: 'Încarcă document',
    uploading: 'Se încarcă...',
    
    generateTitle: 'Generează document',
    generateSubtitle: 'Generează documente noi standarde tehnice folosind AI',
    
    analyticsTitle: 'Tabloul de bord analitic',
    analyticsSubtitle: 'Informații despre utilizarea și performanța sistemului.',
    totalQueries: 'Total interogări',
    avgResponseTime: 'Timp mediu de răspuns',
    dailyQueries: 'Interogări zilnice',
    documentsAccessed: 'Documente accesate',
    queryVolume: 'Volumul interogărilor în timp',
    averageResponseTime: 'Timp mediu de răspuns',
    mostAccessedDocuments: 'Cele mai accesate documente',
    mostPopularQueries: 'Cele mai populare interogări',
    
    completed: 'finalizat',
    processing: 'în procesare',
    errorStatus: 'eroare',
  },
};
