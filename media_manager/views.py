from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import MediaFile, MediaCollection, MediaTag
import json
import mimetypes


@login_required
def media_library(request):
    """Main media library view"""
    media_files = MediaFile.objects.filter(user=request.user)

    # Filter by type
    media_type = request.GET.get('type')
    if media_type:
        media_files = media_files.filter(media_type=media_type)

    # Search
    search = request.GET.get('search')
    if search:
        media_files = media_files.filter(
            Q(file_name__icontains=search) |
            Q(alt_text__icontains=search) |
            Q(caption__icontains=search)
        )

    # Pagination
    paginator = Paginator(media_files, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'media_type': media_type,
        'search': search,
        'total_files': media_files.count(),
    }

    return render(request, 'media_manager/library.html', context)


@login_required
@require_http_methods(["POST"])
def upload_media(request):
    """Handle media file uploads via AJAX"""
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)

    uploaded_file = request.FILES['file']

    # Validate file type
    allowed_types = {
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        'video': ['video/mp4', 'video/webm', 'video/ogg'],
        'audio': ['audio/mp3', 'audio/wav', 'audio/ogg'],
    }

    mime_type = mimetypes.guess_type(uploaded_file.name)[0]
    media_type = None

    for type_name, types in allowed_types.items():
        if mime_type in types:
            media_type = type_name
            break

    if not media_type:
        return JsonResponse({'error': 'Unsupported file type'}, status=400)

    # Create media file
    media_file = MediaFile.objects.create(
        user=request.user,
        original_file=uploaded_file,
        media_type=media_type,
        file_name=uploaded_file.name,
        file_size=uploaded_file.size,
        mime_type=mime_type,
        alt_text=request.POST.get('alt_text', ''),
        caption=request.POST.get('caption', ''),
    )

    return JsonResponse({
        'id': str(media_file.id),
        'file_name': media_file.file_name,
        'media_type': media_file.media_type,
        'file_size': media_file.file_size_human,
        'url': media_file.original_file.url,
        'thumbnail_url': media_file.thumbnail.url if media_file.thumbnail else None,
    })


@login_required
def media_detail(request, media_id):
    """View and edit media file details"""
    media_file = get_object_or_404(MediaFile, id=media_id, user=request.user)

    if request.method == 'POST':
        # Update media file metadata
        media_file.alt_text = request.POST.get('alt_text', '')
        media_file.caption = request.POST.get('caption', '')
        media_file.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

    context = {
        'media_file': media_file,
        'collections': MediaCollection.objects.filter(user=request.user),
        'tags': MediaTag.objects.all(),
    }

    return render(request, 'media_manager/detail.html', context)


@login_required
def collections(request):
    """View and manage media collections"""
    collections = MediaCollection.objects.filter(user=request.user)

    if request.method == 'POST':
        # Create new collection
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        collection = MediaCollection.objects.create(
            user=request.user,
            name=name,
            description=description,
        )

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'id': str(collection.id),
                'name': collection.name,
                'description': collection.description,
                'media_count': collection.media_count,
            })

    context = {
        'collections': collections,
    }

    return render(request, 'media_manager/collections.html', context)


@login_required
def collection_detail(request, collection_id):
    """View collection details and manage media"""
    collection = get_object_or_404(MediaCollection, id=collection_id, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_media':
            media_ids = request.POST.getlist('media_ids')
            media_files = MediaFile.objects.filter(id__in=media_ids, user=request.user)
            collection.media_files.add(*media_files)

        elif action == 'remove_media':
            media_id = request.POST.get('media_id')
            media_file = get_object_or_404(MediaFile, id=media_id, user=request.user)
            collection.media_files.remove(media_file)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

    # Pagination for collection media
    media_files = collection.media_files.all()
    paginator = Paginator(media_files, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'collection': collection,
        'page_obj': page_obj,
        'available_media': MediaFile.objects.filter(user=request.user).exclude(
            id__in=collection.media_files.values_list('id', flat=True)
        )[:20],
    }

    return render(request, 'media_manager/collection_detail.html', context)


@login_required
@require_http_methods(["DELETE"])
def delete_media(request, media_id):
    """Delete a media file"""
    media_file = get_object_or_404(MediaFile, id=media_id, user=request.user)

    # Delete physical files
    if media_file.original_file:
        media_file.original_file.delete()
    if media_file.optimized_file:
        media_file.optimized_file.delete()
    if media_file.thumbnail:
        media_file.thumbnail.delete()

    media_file.delete()

    return JsonResponse({'success': True})


@login_required
def media_stats(request):
    """Get media library statistics"""
    user_media = MediaFile.objects.filter(user=request.user)

    stats = {
        'total_files': user_media.count(),
        'total_size': sum(media.file_size for media in user_media),
        'by_type': {
            'images': user_media.filter(media_type='image').count(),
            'videos': user_media.filter(media_type='video').count(),
            'audio': user_media.filter(media_type='audio').count(),
        },
        'collections': MediaCollection.objects.filter(user=request.user).count(),
    }

    # Convert total size to human readable
    total_size = stats['total_size']
    for unit in ['B', 'KB', 'MB', 'GB']:
        if total_size < 1024.0:
            stats['total_size_human'] = f"{total_size:.1f} {unit}"
            break
        total_size /= 1024.0

    return JsonResponse(stats)
