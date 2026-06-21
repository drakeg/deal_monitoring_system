export const brands = {
  adventures: {
    name: 'Mad Mallards Adventures',
    slug: 'adventures',
    tagline: 'RV, camping, towing, creator gear, and travel-friendly finds.',
    path: '/adventures'
  },
  'personal-training': {
    name: 'Mad Mallard Personal Training',
    slug: 'personal-training',
    tagline: 'Fitness, recovery, home gym, meal prep, and wellness gear.',
    path: '/personal-training'
  },
  solutions: {
    name: 'Mad Mallard Solutions',
    slug: 'solutions',
    tagline: 'Tech, home office, cloud/dev tools, and creator workflow gear.',
    path: '/solutions'
  }
} as const;

export type BrandSlug = keyof typeof brands;
