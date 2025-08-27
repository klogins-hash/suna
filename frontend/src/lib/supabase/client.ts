import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  if (process.env.NEXT_PUBLIC_DISABLE_AUTH === 'true') {
    return {
      auth: {
        getUser: () => Promise.resolve({ data: { user: null }, error: null }),
        getSession: () => Promise.resolve({ data: { session: null }, error: null }),
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
        signOut: () => Promise.resolve({ error: null }),
      },
      from: () => ({
        select: () => Promise.resolve({ data: [], error: null }),
        insert: () => Promise.resolve({ data: null, error: null }),
        update: () => Promise.resolve({ data: null, error: null }),
        delete: () => Promise.resolve({ data: null, error: null }),
        eq: () => ({ data: [], error: null }),
        neq: () => ({ data: [], error: null }),
        gt: () => ({ data: [], error: null }),
        gte: () => ({ data: [], error: null }),
        lt: () => ({ data: [], error: null }),
        lte: () => ({ data: [], error: null }),
        like: () => ({ data: [], error: null }),
        ilike: () => ({ data: [], error: null }),
        is: () => ({ data: [], error: null }),
        in: () => ({ data: [], error: null }),
        contains: () => ({ data: [], error: null }),
        containedBy: () => ({ data: [], error: null }),
        rangeGt: () => ({ data: [], error: null }),
        rangeGte: () => ({ data: [], error: null }),
        rangeLt: () => ({ data: [], error: null }),
        rangeLte: () => ({ data: [], error: null }),
        rangeAdjacent: () => ({ data: [], error: null }),
        overlaps: () => ({ data: [], error: null }),
        textSearch: () => ({ data: [], error: null }),
        match: () => ({ data: [], error: null }),
        not: () => ({ data: [], error: null }),
        or: () => ({ data: [], error: null }),
        filter: () => ({ data: [], error: null }),
        order: () => ({ data: [], error: null }),
        limit: () => ({ data: [], error: null }),
        range: () => ({ data: [], error: null }),
        abortSignal: () => ({ data: [], error: null }),
        single: () => Promise.resolve({ data: null, error: null }),
        maybeSingle: () => Promise.resolve({ data: null, error: null }),
        csv: () => Promise.resolve({ data: '', error: null }),
        geojson: () => Promise.resolve({ data: null, error: null }),
        explain: () => Promise.resolve({ data: null, error: null }),
        rollback: () => Promise.resolve({ data: null, error: null }),
        returns: () => ({ data: [], error: null }),
      }),
      rpc: (functionName: string) => {
        switch (functionName) {
          case 'get_accounts':
            return Promise.resolve({
              data: [
                {
                  account_id: 'mock-personal-account-id',
                  name: 'Personal Account',
                  account_role: 'owner',
                  is_primary_owner: true,
                  slug: 'personal',
                  personal_account: true,
                },
                {
                  account_id: 'mock-team-account-id',
                  name: 'Demo Team',
                  account_role: 'owner',
                  is_primary_owner: true,
                  slug: 'demo-team',
                  personal_account: false,
                }
              ],
              error: null
            });
          case 'get_personal_account':
            return Promise.resolve({
              data: {
                account_id: 'mock-personal-account-id',
                name: 'Personal Account',
                account_role: 'owner',
                is_primary_owner: true,
                slug: 'personal',
                personal_account: true,
              },
              error: null
            });
          default:
            return Promise.resolve({ data: null, error: null });
        }
      },
      storage: {
        from: () => ({
          upload: () => Promise.resolve({ data: null, error: null }),
          download: () => Promise.resolve({ data: null, error: null }),
          list: () => Promise.resolve({ data: [], error: null }),
          remove: () => Promise.resolve({ data: null, error: null }),
          move: () => Promise.resolve({ data: null, error: null }),
          copy: () => Promise.resolve({ data: null, error: null }),
          createSignedUrl: () => Promise.resolve({ data: null, error: null }),
          createSignedUrls: () => Promise.resolve({ data: [], error: null }),
          getPublicUrl: () => ({ data: { publicUrl: '' } }),
        }),
      },
      realtime: {
        channel: () => ({
          on: () => ({}),
          subscribe: () => Promise.resolve('ok'),
          unsubscribe: () => Promise.resolve('ok'),
        }),
      },
    } as any;
  }

  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}
