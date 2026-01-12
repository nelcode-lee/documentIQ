/** Custom hook for authentication. */

import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [isAuthenticated] = useState(false);
  const [user] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication status
    // This will be implemented with Azure AD integration
    setLoading(false);
  }, []);

  return { isAuthenticated, user, loading };
};
