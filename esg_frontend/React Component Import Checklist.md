# React Component Import Checklist

## ⚠️ CRITICAL: Always Check Icon Imports

### Common Issue: Missing Icon Imports
**Problem**: Using icons in JSX without importing them from lucide-react
**Error**: `ReferenceError: [IconName] is not defined`

### ✅ Solution: Complete Import Checklist

#### 1. **Before Using Any Icon, Import It**
```javascript
// ❌ WRONG - Using icon without import
<AlertCircle className="h-4 w-4" />

// ✅ CORRECT - Import first, then use
import { AlertCircle } from 'lucide-react';
<AlertCircle className="h-4 w-4" />
```

#### 2. **Common Icons That Are Often Forgotten**
- `AlertCircle` - Used in error alerts
- `Info` - Used in info alerts  
- `CheckCircle` - Used for success states
- `Clock` - Used for pending states
- `Archive` - Used for archived items
- `RotateCcw` - Used for refresh/restore actions
- `ChevronDown` - Used in dropdowns
- `Eye` - Used for view actions

#### 3. **Complete Import Pattern**
```javascript
import { 
  // Basic actions
  Plus, Edit, Trash2, Save, Cancel,
  // Navigation
  ChevronDown, ChevronUp, ChevronLeft, ChevronRight,
  // Status indicators  
  CheckCircle, AlertCircle, Info, Clock, Archive,
  // Common actions
  Search, Filter, History, Eye, RotateCcw,
  // Data visualization
  BarChart3, TrendingUp, Target, Users
} from 'lucide-react';
```

#### 4. **UI Component Imports**
```javascript
// Always import ALL UI components used
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
```

### 🔍 **Pre-Deployment Checklist**

#### Before Saving Any Component:
1. **Scan for all `<IconName` patterns in JSX**
2. **Verify each icon is imported from lucide-react**
3. **Check all UI components are imported**
4. **Test component compilation**

#### Quick Search Commands:
```bash
# Find all icon usage in component
grep -o '<[A-Z][a-zA-Z]*' ComponentName.jsx

# Find missing imports
grep -o '<[A-Z][a-zA-Z]*' ComponentName.jsx | sort -u
```

### 📝 **Standard Import Template**

```javascript
import React, { useState, useEffect } from 'react';

// UI Components (import ALL that are used)
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';

// Icons (import ALL that are used - check JSX carefully)
import { 
  Plus, Search, Edit, Trash2, Filter, History, 
  ChevronDown, Eye, CheckCircle, Clock, Archive, 
  RotateCcw, Info, AlertCircle, Save, Cancel,
  BarChart3, TrendingUp, Target, Users, FolderOpen
} from 'lucide-react';
```

### 🚨 **Remember**: 
- **Every icon used in JSX MUST be imported**
- **Check the entire component before saving**
- **Test compilation after adding new icons**
- **Use this checklist for every React component**

