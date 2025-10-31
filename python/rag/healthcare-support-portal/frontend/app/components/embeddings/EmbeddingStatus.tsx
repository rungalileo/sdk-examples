import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';

interface EmbeddingStatusProps {
  documentId: number;
  hasEmbeddings: boolean;
  embeddingCount?: number;
  onRegenerate?: () => Promise<void>;
  canRegenerate?: boolean;
}

export function EmbeddingStatus({ 
  documentId, 
  hasEmbeddings, 
  embeddingCount = 0,
  onRegenerate,
  canRegenerate = false
}: EmbeddingStatusProps) {
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [regenerateStatus, setRegenerateStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleRegenerate = async () => {
    if (!onRegenerate) return;
    
    setIsRegenerating(true);
    setRegenerateStatus('idle');
    
    try {
      await onRegenerate();
      setRegenerateStatus('success');
      setTimeout(() => setRegenerateStatus('idle'), 3000);
    } catch (error) {
      setRegenerateStatus('error');
      setTimeout(() => setRegenerateStatus('idle'), 3000);
    } finally {
      setIsRegenerating(false);
    }
  };

  const getBadgeVariant = () => {
    if (regenerateStatus === 'success') return 'success';
    if (regenerateStatus === 'error') return 'destructive';
    if (!hasEmbeddings) return 'secondary';
    return 'default';
  };

  const getBadgeIcon = () => {
    if (isRegenerating) return <Loader2 className="mr-1 h-3 w-3 animate-spin" />;
    if (regenerateStatus === 'success') return <CheckCircle className="mr-1 h-3 w-3" />;
    if (regenerateStatus === 'error') return <AlertCircle className="mr-1 h-3 w-3" />;
    if (hasEmbeddings) return <CheckCircle className="mr-1 h-3 w-3" />;
    return <AlertCircle className="mr-1 h-3 w-3" />;
  };

  const getBadgeText = () => {
    if (isRegenerating) return 'Regenerating...';
    if (regenerateStatus === 'success') return 'Regenerated!';
    if (regenerateStatus === 'error') return 'Failed';
    if (hasEmbeddings) return `${embeddingCount} embeddings`;
    return 'No embeddings';
  };

  return (
    <div className="flex items-center space-x-2">
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge variant={getBadgeVariant()} className="text-xs">
              {getBadgeIcon()}
              {getBadgeText()}
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p className="text-xs">
              {hasEmbeddings 
                ? `Document has ${embeddingCount} vector embeddings for AI search`
                : 'No embeddings generated yet - document won\'t appear in AI searches'}
            </p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      {canRegenerate && onRegenerate && (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRegenerate}
                disabled={isRegenerating}
                className="h-7 px-2"
              >
                <RefreshCw className={cn("h-3 w-3", isRegenerating && "animate-spin")} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              <p className="text-xs">Regenerate embeddings for this document</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )}
    </div>
  );
}