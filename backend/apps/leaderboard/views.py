from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Snapshot, Entry
from .serializers import SnapshotSerializer, SnapshotDetailSerializer, EntrySerializer, MyRankSerializer


class SnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """랭킹 스냅샷 API"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Snapshot.objects.filter(is_active=True)
        
        period = self.request.query_params.get('period')
        language = self.request.query_params.get('language')
        mode = self.request.query_params.get('mode')
        
        if period:
            queryset = queryset.filter(period=period)
        if language:
            queryset = queryset.filter(language=language)
        if mode:
            queryset = queryset.filter(mode=mode)
        
        return queryset.order_by('-generated_at')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SnapshotDetailSerializer
        return SnapshotSerializer
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """최신 랭킹 조회"""
        period = request.query_params.get('period', 'weekly')
        language = request.query_params.get('language', 'all')
        
        snapshot = self.get_queryset().filter(
            period=period    
        ).first()
        
        if not snapshot:
            return Response({'detail': '랭킹이 아직 생성되지 않았습니다.'}, status=404)
        
        serializer = SnapshotDetailSerializer(snapshot)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """내 순위 조회"""
        if not request.user.is_authenticated:
            return Response({'detail': '로그인이 필요합니다.'}, status=401)
        
        period = request.query_params.get('period', 'weekly')
        language = request.query_params.get('language', 'all')
        
        snapshot = self.get_queryset().filter(period=period).first()
        
        if not snapshot:
            return Response({'detail': '랭킹이 아직 생성되지 않았습니다.'}, status=404)
        
        # 내 엔트리 찾기
        my_entry = snapshot.entries.filter(user=request.user).first()
        
        # 근처 랭커 (내 순위 ±2)
        neighbors = []
        if my_entry:
            neighbors = snapshot.entries.filter(
                rank__gte=max(1, my_entry.rank - 2),
                rank__lte=my_entry.rank + 2
            ).exclude(user=request.user)
        
        data = {
            'snapshot': SnapshotSerializer(snapshot).data,
            'my_entry': EntrySerializer(my_entry).data if my_entry else None,
            'neighbors': EntrySerializer(neighbors, many=True).data,
        }
        
        return Response(data)


class EntryViewSet(viewsets.ReadOnlyModelViewSet):
    """랭킹 엔트리 API"""
    serializer_class = EntrySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        snapshot_id = self.request.query_params.get('snapshot')
        queryset = Entry.objects.all()
        
        if snapshot_id:
            queryset = queryset.filter(snapshot_id=snapshot_id)
        
        return queryset.order_by('rank')[:100]  # 상위 100명만
