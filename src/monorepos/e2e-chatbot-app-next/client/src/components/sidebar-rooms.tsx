import { useLocation, useNavigate } from 'react-router-dom';
import { LAB_ROOMS } from '@chat-template/core/lab-rooms';
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupContentHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { DbIcon } from '@/components/ui/db-icon';
import { DatabaseIcon } from '@/components/icons';

export function SidebarRooms() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setOpenMobile } = useSidebar();

  return (
    <SidebarGroup>
      <SidebarGroupContentHeader>Salas Genie</SidebarGroupContentHeader>
      <SidebarGroupContent>
        <SidebarMenu>
          {LAB_ROOMS.map((room) => {
            const href = `/room/${room.alias}`;
            const isActive = location.pathname === href;
            return (
              <SidebarMenuItem key={room.alias}>
                <SidebarMenuButton
                  type="button"
                  isActive={isActive}
                  data-testid={`room-${room.alias}`}
                  className="h-8 cursor-pointer"
                  onClick={() => {
                    setOpenMobile(false);
                    navigate(href);
                  }}
                >
                  <DbIcon icon={DatabaseIcon} size={16} color="default" />
                  <span className="group-data-[collapsible=icon]:hidden">
                    {room.title}
                  </span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            );
          })}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
