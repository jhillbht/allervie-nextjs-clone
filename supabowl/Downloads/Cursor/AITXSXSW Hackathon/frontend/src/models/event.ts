
export type EventTag = 'energetic' | 'informative';

export interface Event {
  id: string;
  name: string;
  description: string;
  tags: EventTag[];
  date: string;
  location: string;
  image?: string;
}
