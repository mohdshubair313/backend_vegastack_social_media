# posts/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import Post
from .serializers import PostSerializer
from .permissions import IsOwnerOrReadOnly

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    """
    CRUD for posts:
    - Create: POST /api/posts/
    - Retrieve: GET /api/posts/{id}/
    - Update: PUT/PATCH /api/posts/{id}/
    - Delete: DELETE /api/posts/{id}/
    - List: GET /api/posts/?page=1&page_size=20
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content", "author__username"]
    ordering_fields = ["created_at", "like_count", "comment_count"]

    def get_queryset(self):
        qs = Post.objects.filter(is_active=True).select_related("author")
        # admins can view inactive posts if they add ?show_inactive=1
        if getattr(self.request, "user", None) and self.request.user.is_staff and self.request.GET.get("show_inactive") == "1":
            qs = Post.objects.all().select_related("author")
        return qs

    def perform_create(self, serializer):
        # pass author explicitly; serializer.create handles being passed author safely
        serializer.save(author=self.request.user, is_active=True)
