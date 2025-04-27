import { useContext } from 'react';
import { SupabaseContext } from '../contexts/SupabaseContext';

export const useSupabase = () => useContext(SupabaseContext); 