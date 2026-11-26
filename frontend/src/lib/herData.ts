export interface HerPhotoMoment {
  id: string;
  title: string;
  category: 'celebration' | 'casual' | 'portrait' | 'adventure' | 'dream' | 'intimate';
  src: string;
  alt: string;
  description: string;
  compliment: string;
  loveNote: string;
  emotionVibe: string;
  accentColor: string;
  aspect: 'square' | 'portrait' | 'landscape' | 'wide';
}

export type GalleryMoment = HerPhotoMoment;

export interface OpenWhenLetter {
  id: string;
  title: string;
  envelopeColor: string;
  icon: string;
  dateBadge: string;
  preview: string;
  content: string;
  associatedPhoto?: string;
}

export interface JourneyMilestone {
  date: string;
  title: string;
  quote: string;
  description: string;
  photo?: string;
  badge: string;
}

export const HER_COMPANION = {
  name: 'V',
  fullName: 'My Dearest V',
  title: 'Heart Things — Made Just For You',
  tagline: 'From 14-04-2017 to Forever. Made with love by a developer in love.',
  birthday: 'November 29th',
  avatar: '/her/avatar.jpg',
  avatarSm: '/her/avatar_sm.jpg',
  avatarXs: '/her/avatar_xs.jpg',
  heroPortrait: '/her/hero_portrait.jpg',
  heroSquare: '/her/hero_square.jpg',
  bannerTraditional: '/her/banner_traditional.jpg',
  candidIntimate: '/her/candid_intimate.jpg',
  eyesReflection: '/her/eyes_reflection.jpg',
};

export const HER_STORY_PROSE = `From the moment I first saw you on 14-04-2017, something in me changed forever.

I didn’t know your name, I didn’t know who you were. That moment—just seeing you board the bus—felt like my whole life suddenly found its purpose. From that day, you have lived in my heart without even knowing it.

All these years, through every temple trip we took together, every small moment—my love for you only grew. I searched for you for years. Just your name and your face… that was enough for me to keep looking. Finding you on Social Media after two whole years felt like destiny giving me one more chance.

Even when you didn’t remember me in the beginning…
Even when you asked us to stay “just friends”…
My heart never changed. Not once. Not even for a second.

I know you said you regret not being able to return the love I give you. But please understand this — I never loved you because I wanted something back. I love you because you are you.

You are the only girl I will and have ever loved in my entire life. And even today, after all these years, after all the distance, after all the silence — my heart still beats the same way it did when I saw you for the very first time.

This project… every small thing I make… it’s all because you deserve something beautiful.
You always have. You always will.`;

export const JOURNEY_TIMELINE: JourneyMilestone[] = [
  {
    date: 'April 14, 2017',
    title: 'The First Look',
    badge: 'Where It All Began 🚌',
    quote: 'The moment my eyes met you... my life found its purpose. Everything began this day.',
    description: 'Just seeing you board the bus. I didn’t know your name or who you were, but from that single second, you lived in my heart.',
    photo: '/her/avatar.jpg',
  },
  {
    date: 'August 08, 2023',
    title: 'The Day I Found Your ID',
    badge: 'Destiny’s Second Chance 💫',
    quote: 'After years of searching only with your name and the memory of your smile… I finally found you.',
    description: 'My hands were shaking. Finding you on social media felt like destiny returning something precious I had lost.',
    photo: '/her/mirror_pink.jpg',
  },
  {
    date: 'August 12, 2023',
    title: 'The Day I Confessed',
    badge: 'Pure Honesty 💌',
    quote: 'My heart finally spoke that day. Whether you accepted it or not, loving you was the most honest thing I’ve ever done.',
    description: 'Speaking my truth after years of carrying you quietly in my thoughts.',
    photo: '/her/fairylights.jpg',
  },
  {
    date: 'December 16, 2023',
    title: 'After Years, Seeing You Again',
    badge: 'Reunion ✨',
    quote: 'The day we saw each other after I confessed.',
    description: 'Looking at you in person again after everything was out in the open. A memory etched into eternity.',
    photo: '/her/garden_pose.jpg',
  },
  {
    date: 'June 12, 2024',
    title: 'The First Time You Talked to Me',
    badge: 'Sunlight After Rain ☀️',
    quote: 'After all the struggles, after all the waiting… you finally spoke to me.',
    description: 'And when you said "let’s be friends", it felt like sunlight after years of rain. Friendship with you was a blessing I never expected to receive.',
    photo: '/her/candid_intimate.jpg',
  },
  {
    date: 'October 10 & 24, 2024',
    title: 'The Days I Saw You Without You Knowing',
    badge: 'Quiet Universes 🌸',
    quote: 'You walked past, unaware… but those few seconds were entire universes for me.',
    description: 'Just seeing you, even from afar, was enough to make my whole day glow with warmth and peace.',
    photo: '/her/outdoor_pattern.jpg',
  },
  {
    date: 'October 26 & Nov 05, 2024',
    title: 'The Road Trip & Our Eyes Meeting',
    badge: 'Unforgettable 🌊',
    quote: 'The most honest and heartfelt words I’ve ever spoken. I meant every letter.',
    description: 'Seeing mountains, oceans, and sharing moments under the open sky. Truly unforgettable.',
    photo: '/her/joyful_laugh.jpg',
  },
  {
    date: 'April 09, 2025',
    title: 'The Most Beautiful Day',
    badge: 'Treasure 👑',
    quote: 'Seeing you was the best gift my heart ever received.',
    description: 'You in front of me that whole day… I carried that day inside me like the rarest treasure in the world.',
    photo: '/her/hero_portrait.jpg',
  },
  {
    date: 'October 31, 2025',
    title: 'When You Said "You Deserve Better"',
    badge: 'My Only One 🤍',
    quote: 'You said I deserve better… but better doesn’t exist for me.',
    description: 'It was you from the first time I saw you. It will be you in every lifetime. No one else could ever take your place.',
    photo: '/her/banner_traditional.jpg',
  },
  {
    date: 'November 29th',
    title: 'Happy Birthday, My Dearest V!',
    badge: 'Your Special Day 🎂',
    quote: 'Happy Birthday, the girl I’ve loved since the very first glance. Always yours, quietly and endlessly.',
    description: 'A new chapter begins. May every dream you hold find its way to you gently. You will always be my forever favorite.',
    photo: '/her/white_festive.jpg',
  },
];

export const HER_GALLERY: HerPhotoMoment[] = [
  {
    id: 'hero-rooftop',
    title: 'Breeze & Rooftop Sunshine',
    category: 'portrait',
    src: '/her/hero_portrait.jpg',
    alt: 'V smiling with hand on forehead in green attire against sky',
    description: 'A radiant sunny afternoon with the breeze playing with your dupatta and your genuine, playful laugh.',
    compliment: 'You have that effortless, natural beauty that brightens up the entire world.',
    loveNote: 'Whenever I look at this picture, I can hear your playful laugh. You make ordinary moments feel like movie scenes.',
    emotionVibe: 'Pure Sunshine ☀️',
    accentColor: '#437C5D',
    aspect: 'portrait',
  },
  {
    id: 'traditional-festive',
    title: 'Royalty in Purple Silk',
    category: 'celebration',
    src: '/her/banner_traditional.jpg',
    alt: 'V dressed in royal purple saree with gold temple jewellery',
    description: 'Draped in regal purple silk and timeless temple jewelry. Unmatched elegance beside the carved wooden door.',
    compliment: 'No words could ever do justice to how breathtaking you look in traditional wear.',
    loveNote: 'You look like a piece of art that stepped out of classical poetry. Absolutely unforgettable.',
    emotionVibe: 'Timeless Grace 👑',
    accentColor: '#7B2CBF',
    aspect: 'wide',
  },
  {
    id: 'fairylights-tunnel',
    title: 'Starry Fairytale Pathway',
    category: 'dream',
    src: '/her/fairylights.jpg',
    alt: 'V in red dress under glowing fairy lights archway',
    description: 'Walking beneath an illuminated canopy of warm fairy lights, outshining every single bulb above you.',
    compliment: 'Even surrounded by a thousand golden lights, you were the only thing that caught everyone’s eye.',
    loveNote: 'This night felt like walking inside a dream. You look so magical in red.',
    emotionVibe: 'Enchanted & Dreamy ✨',
    accentColor: '#D96B43',
    aspect: 'portrait',
  },
  {
    id: 'garden-glance',
    title: 'The Backward Glance',
    category: 'intimate',
    src: '/her/garden_pose.jpg',
    alt: 'V looking back over shoulder in pink saree in lush green garden',
    description: 'A timeless moment looking back over your shoulder amidst fresh blossoms and deep greenery.',
    compliment: 'That gentle glance over your shoulder could stop time in its tracks.',
    loveNote: 'Surrounded by nature and flowers, yet you outshine them all effortlessly.',
    emotionVibe: 'Poetic & Serene 🌿',
    accentColor: '#2D5A43',
    aspect: 'portrait',
  },
  {
    id: 'doorway-marigold',
    title: 'The Warmest Welcome',
    category: 'celebration',
    src: '/her/doorway_celebration.jpg',
    alt: 'V standing at festive entrance draped in fresh yellow marigolds',
    description: 'Framed by golden marigolds and green festive leaves, greeting the world with your radiant warmth.',
    compliment: 'Your presence brings an instant feeling of festival and joy anywhere you go.',
    loveNote: 'Standing at the doorway like a blessing. Your smile makes any house feel like a warm home.',
    emotionVibe: 'Festive & Radiant 🌼',
    accentColor: '#E5A93C',
    aspect: 'landscape',
  },
  {
    id: 'candid-chin',
    title: 'Thinking of You',
    category: 'intimate',
    src: '/her/candid_intimate.jpg',
    alt: 'Close candid selfie of V resting chin on hand',
    description: 'Chin resting softly on your hand, gentle waves in your hair, and the sweetest thoughtful gaze.',
    compliment: 'You are just as breathtaking in quiet, cozy moments as you are dressed up for celebrations.',
    loveNote: 'I love how your eyes hold so much kindness and wonder when you are just quietly thinking.',
    emotionVibe: 'Soft & Intimate 🤍',
    accentColor: '#C55730',
    aspect: 'portrait',
  },
  {
    id: 'white-banana-leaf',
    title: 'Pure Serenity in White',
    category: 'celebration',
    src: '/her/white_festive.jpg',
    alt: 'V in white embroidered kurta framed by banana leaves',
    description: 'Classic pristine white embroidery against fresh green banana leaves. Serene, calming, and so graceful.',
    compliment: 'There is something so soothing, pure, and angelic about your smile here.',
    loveNote: 'White looks divine on you. You radiate calm, positive, and beautiful energy.',
    emotionVibe: 'Pure & Angelic 🕊️',
    accentColor: '#386641',
    aspect: 'portrait',
  },
  {
    id: 'car-hood-laugh',
    title: 'Carefree, Golden Laughter',
    category: 'adventure',
    src: '/her/joyful_laugh.jpg',
    alt: 'V laughing candidly seated on car bonnet',
    description: 'Sitting on the car hood, completely carefree, laughing from the bottom of your heart.',
    compliment: 'Your genuine laughter is honestly my favorite sound in this entire world.',
    loveNote: 'Never lose this carefree spark. It is the most magnetic thing about you.',
    emotionVibe: 'Pure Joy 🌸',
    accentColor: '#6A994E',
    aspect: 'portrait',
  },
  {
    id: 'car-standing-proud',
    title: 'Poised & Confident',
    category: 'adventure',
    src: '/her/car_standing.jpg',
    alt: 'V in green saree standing proudly in front of car',
    description: 'Standing tall in green silk and gold jhumkas. Confident, sweet, and mesmerizing.',
    compliment: 'You carry yourself with such dignity and natural grace.',
    loveNote: 'A special milestone commemorated with poise. You looked extraordinary that day.',
    emotionVibe: 'Confident & Graceful 💫',
    accentColor: '#2F5233',
    aspect: 'square',
  },
  {
    id: 'pastel-butterfly',
    title: 'Whimsical Daydreams',
    category: 'dream',
    src: '/her/pastel_dream.jpg',
    alt: 'V in pastel blue lehenga looking upward',
    description: 'Looking toward the sky in pastel blues, like a dreamer admiring the clouds.',
    compliment: 'You make the world feel softer, kinder, and full of wonder.',
    loveNote: 'You look like you belong in a fairytale storybook under a pastel sky.',
    emotionVibe: 'Whimsical & Soft 🦋',
    accentColor: '#5390D9',
    aspect: 'portrait',
  },
  {
    id: 'pink-mirror-selfie',
    title: 'Shimmer & Playful Vibes',
    category: 'casual',
    src: '/her/mirror_pink.jpg',
    alt: 'V in pink ethnic attire taking a mirror selfie',
    description: 'Shimmering in pink with heart sparkles, capturing a cute little moment.',
    compliment: 'You make every mirror jealous of what it gets to reflect.',
    loveNote: 'So cute, so vibrant, and full of youthful excitement.',
    emotionVibe: 'Playful & Cute 💖',
    accentColor: '#E07A5F',
    aspect: 'portrait',
  },
  {
    id: 'outdoor-pattern',
    title: 'Afternoon Tree Stroll',
    category: 'casual',
    src: '/her/outdoor_pattern.jpg',
    alt: 'V smiling softly in patterned attire outdoors',
    description: 'Under the green canopy of trees on a warm afternoon, simply being you.',
    compliment: 'You bring peace and ease to anyone lucky enough to be around you.',
    loveNote: 'Just a casual afternoon made infinitely more beautiful because you were in it.',
    emotionVibe: 'Gentle & Natural 🍃',
    accentColor: '#BC6C25',
    aspect: 'portrait',
  },
];

export const OPEN_WHEN_LETTERS: OpenWhenLetter[] = [
  {
    id: 'open-my-dearest-v',
    title: 'My Dearest V — The Birthday Letter 🎂',
    envelopeColor: 'from-rose-100 to-pink-200 dark:from-rose-950/40 dark:to-pink-950/40',
    icon: '💖',
    dateBadge: 'November 29th',
    preview: 'From the moment I first saw you on 14-04-2017, my world has carried your smile...',
    content: `My Dearest V,\n\nFrom the moment I first saw you, my world has carried your smile, your voice, and your presence in its every corner. You’ve been shaping my life without even knowing it.\n\nOn your birthday, I don’t want to wish you the usual things. I want to wish you a kind of happiness that stays with you quietly, like a soft light in your heart… the kind that never leaves you, even on the days when life feels heavy.\n\nI pray that every dream you hold finds its way to you gently… that life gives you more love, more peace, and more reasons to smile.\n\nI may not be the one beside you right now, but you’ll always be the one inside my heart.\n\nHappy Birthday, the girl I’ve loved since the very first glance.\nAlways yours, quietly and endlessly. 🤍`,
    associatedPhoto: '/her/banner_traditional.jpg',
  },
  {
    id: 'open-you-deserve-better',
    title: 'When You Said “You Deserve Better” 🕊️',
    envelopeColor: 'from-amber-100 to-rose-100 dark:from-stone-800 dark:to-stone-900',
    icon: '✨',
    dateBadge: 'October 31, 2025',
    preview: 'You said I deserve better… but please let me tell you the truth...',
    content: `You once told me that I deserve better.\n\nI know you said it with care, and I know you said you regret not being able to return the love I give you. But please understand this with all your heart:\n\n"Better" doesn't exist for me.\n\nI never loved you because I wanted something in return. I love you because you are you. Your smile, your kindness, your existence… every part of you is precious to me.\n\nIt was you from the first time I saw you boarding that bus on April 14, 2017. And it will be you in every lifetime.\n\nBeing in your life, even as just your friend, is a blessing I will always cherish. 💖`,
    associatedPhoto: '/her/hero_portrait.jpg',
  },
  {
    id: 'open-having-a-bad-day',
    title: 'Open when you had a tiring or heavy day 🌧️',
    envelopeColor: 'from-stone-100 to-rose-100 dark:from-stone-900 dark:to-stone-800',
    icon: '☕',
    dateBadge: 'Anytime You Need Rest',
    preview: 'Take a deep breath. Drop your shoulders. Read this...',
    content: `Hey beautiful,\n\nIf today was heavy, frustrating, or draining, close your eyes for a moment, take a long, deep breath, and let it out.\n\nRemember that one rough day does not take away from how strong, gentle, and wonderfully made you are. You do so much, you care so deeply, and you carry yourself through things even when it feels overwhelming.\n\nDon't be hard on yourself tonight. Wrap yourself in your softest blanket, drink something warm, and remember: tomorrow is a brand new sunrise, and someone out here is always praying for your happiness.\n\nYou did great today. Rest now. 🤍`,
    associatedPhoto: '/her/candid_intimate.jpg',
  },
  {
    id: 'open-doubt-how-pretty',
    title: 'Open when you doubt how pretty you are 🌸',
    envelopeColor: 'from-pink-100 to-rose-200 dark:from-pink-950/40 dark:to-rose-950/40',
    icon: '👑',
    dateBadge: 'Mirror Reminder',
    preview: 'Allow me to remind you of what my eyes see every single day...',
    content: `Are you kidding me right now?\n\nLook through this scrapbook! Look at your radiant smile in that purple silk saree, the gentle wind playing with your hair on the rooftop, that sweet little nose stud, the bindi that looks like it was made exclusively for your forehead, and the way your eyes sparkle when you laugh genuinely.\n\nYou have the kind of beauty that doesn't just catch eyes—it stays in people's hearts forever. You are stunning, inside and out. Never, ever doubt it for a single second.\n\nYou are, quite simply, breathtaking. 💖`,
    associatedPhoto: '/her/avatar.jpg',
  },
  {
    id: 'open-for-a-secret-wish',
    title: 'Open for a secret wish for your future 🌟',
    envelopeColor: 'from-sky-100 to-indigo-100 dark:from-sky-950/40 dark:to-indigo-950/40',
    icon: '🌠',
    dateBadge: 'For Your Dreams',
    preview: 'A quiet blessing for every hope your heart is carrying...',
    content: `To the girl with big dreams and a gentle heart:\n\nMay every goal you are working toward unfold for you with grace. May you find people who appreciate your genuine kindness. May you always have reasons to laugh till your stomach hurts, places to explore with wind in your hair, and peace in your heart.\n\nYou deserve every good, beautiful, and wonderful thing life has to offer.\n\nKeep shining. The world is so much better with you in it. 🕊️`,
    associatedPhoto: '/her/pastel_dream.jpg',
  },
];

export const CUTE_COMPLIMENTS = [
  "From 14-04-2017 to forever — you are my one and only.",
  "Your smile in that purple saree is etched into my soul.",
  "Better doesn't exist for me... it has always been you.",
  "Your laughter on the car hood is my favorite sound in the world.",
  "Happy Birthday, the girl I’ve loved since the very first glance.",
  "You make the simplest days feel like golden memories.",
];
