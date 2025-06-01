export interface Demo {
  id: string;
  title: string;
  date: string;
  salesRep: string;
  status: 'Ready' | 'Processing' | 'Failed';
  micrositeUrl?: string;
}

export type ActionType = 'view' | 'share' | 'regenerate' | 'delete';